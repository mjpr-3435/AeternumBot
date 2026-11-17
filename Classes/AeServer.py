from __future__ import annotations

import json
import re
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING

from Banners.MembersInfo.Whitelist import update_player_date
from Classes.config import AeternumConfig
from dismanager.core.managed_process import BackupEntry, ManagedProcess
from Utils.minecraft_text import hover_and_suggest
from Utils.rcon import RconError, ensure_rcon_properties, rcon_execute

if TYPE_CHECKING:
    from dismanager.classes import DisManagerClient

_PLAYER_LOGIN_RE = re.compile(r'(.*?) logged in with entity id')
_PLAYER_LEFT_RE = re.compile(r'(.*?) left the game')


class AeServer:
    """Minecraft server state, tellraw helpers, and game-event dispatcher wrapping a ``ManagedProcess``."""

    process: ManagedProcess
    config: AeternumConfig
    admins: tuple[str, ...]
    prefix: str
    omit_crash_report_relay: bool
    stop_signal_received: bool
    online_players: list[str]
    bots: list[str]
    rcon_port: int | None
    rcon_password: str

    def __init__(self, process: ManagedProcess, config: AeternumConfig) -> None:
        self.process                 = process
        self.config                  = config
        self.admins                  = config.admins
        self.prefix                  = process.client.config.bot_prefix
        self.omit_crash_report_relay = False
        self.stop_signal_received    = False
        self.online_players          = []
        self.bots                    = []
        self.rcon_port               = None
        self.rcon_password           = config.rcon_password
        self._configure_rcon()

    # --- Internal Behaviour ---

    def _configure_rcon(self) -> None:
        for candidate in (self.path / 'server.properties', self.path / 'server' / 'server.properties'):
            rcon_port = ensure_rcon_properties(candidate, password=self.rcon_password, port_offset=20)
            if rcon_port is not None:
                self.rcon_port = rcon_port
                return

    async def _handle_info_line(self, log: str) -> None:
        if any(f'<{player}>' in log for player in self.online_players):
            player = log[log.index('<') + 1 : log.index('>')]
            message = log[log.index('>') + 1 :].strip()
            await self.call_plugins('on_mc_player_message', player, message)
            if message.startswith(self.prefix):
                await self.call_plugins('on_mc_player_command', player, message)
            return

        if 'logged in with entity id' in log:
            match = _PLAYER_LOGIN_RE.search(log)
            if match is None:
                return
            player_and_ip = match.group(1).strip().split(' ')[-1]
            player = player_and_ip.split('[')[0]
            local = player_and_ip.removeprefix(player) == '[local]'

            if local and player not in self.bots:
                self.bots.append(player)
            elif not local and player not in self.online_players:
                self.online_players.append(player)
                update_player_date(player)

            await self.call_plugins('on_mc_player_join', player)
            return

        if log.endswith('left the game'):
            match = _PLAYER_LEFT_RE.search(log)
            if match is None:
                return
            formatted_player = match.group(1).strip().split(' ')[-1]
            left_player = next((p for p in self.bots + self.online_players if p == formatted_player), None)
            if left_player in self.bots:
                self.bots.remove(left_player)
            elif left_player in self.online_players:
                self.online_players.remove(left_player)
            await self.call_plugins('on_mc_player_left', left_player)
            return

        if 'Starting minecraft server' in log:
            self.bots = []
            self.online_players = []
            await self.call_plugins('on_mc_starting')
        elif log.endswith('For help, type "help"'):
            await self.call_plugins('on_mc_ready')
        elif log.endswith('Stopping server'):
            self.stop_signal_received = True
            await self.call_plugins('on_mc_stopping')
        elif log.endswith('ThreadedAnvilChunkStorage: All dimensions are saved') and self.stop_signal_received:
            self.bots = []
            self.online_players = []
            self.stop_signal_received = False
            await self.call_plugins('on_mc_stopped')

    # --- Public API ---

    # Properties

    @property
    def name(self) -> str:
        """Return the underlying process name."""
        return self.process.name

    @property
    def path(self) -> Path:
        """Return the process working directory."""
        return self.process.path

    @property
    def path_plugins(self) -> Path:
        """Return the ``<process>/.plugins`` directory."""
        return self.process.path / '.plugins'

    @property
    def client(self) -> DisManagerClient:
        """Return the owning ``DisManagerClient``."""
        return self.process.client

    # Lifecycle & Process Control

    def is_running(self) -> bool:
        """Return whether the wrapped OS process is running."""
        return self.process.is_running()

    def execute(self, command: str) -> bool:
        """Send a command line to the wrapped process console."""
        return self.process.execute(command)

    def start(self) -> bool:
        """Start the wrapped process."""
        return self.process.start()

    def stop(self) -> bool:
        """Request a graceful stop on the wrapped process."""
        return self.process.stop()

    def kill(self) -> bool:
        """Force-kill the wrapped process tree."""
        return self.process.kill()

    async def restart(self) -> bool:
        """Restart the wrapped process."""
        return await self.process.restart()

    # Console & Logs

    def last_logs(self, *, limit: int = 40) -> list[str]:
        """Return up to the last ``limit`` log lines from the recent buffer."""
        return self.process.last_logs(limit=limit)

    # Backups

    def list_backups(self) -> list[BackupEntry]:
        """Return existing backups for the wrapped process."""
        return self.process.list_backups()

    def make_backup(
        self,
        on_progress: Callable[[int, int], None] | None = None,
        *,
        force: bool = False,
    ) -> Path:
        """Create a rotating backup of the wrapped process."""
        return self.process.make_backup(on_progress, force=force)

    # Plugins & Minecraft

    async def call_plugins(self, event_name: str, *args: object) -> None:
        """Dispatch a custom Minecraft event to active plugins of this process."""
        await self.process.call_plugins(event_name, *args)

    async def on_log(self, log: str) -> None:
        """Parse a Minecraft console log line and dispatch game events to plugins."""
        if 'INFO]: ' in log:
            await self._handle_info_line(log)
        elif 'ERROR]: ' in log and log.endswith('Considering it to be crashed, server will forcibly shutdown.'):
            await self.call_plugins('on_mc_crash')

    def send_response(
        self,
        target: str,
        message: str | list[str],
        *,
        colour: str = 'gray',
    ) -> None:
        """Send one or more colored ``tellraw`` messages to ``target``."""
        lines = [message] if isinstance(message, str) else message
        for msg in lines:
            payload = json.dumps({'text': msg, 'color': colour}, ensure_ascii=False)
            self.execute(f'tellraw {target} {payload}')

    def is_command(self, message: str, command: str) -> bool:
        """Return whether ``message`` invokes ``<prefix><command>``."""
        return f'{message} '.startswith(f'{self.prefix}{command} ')

    def show_command(self, target: str, command: str, description: str) -> None:
        """Display a clickable/hoverable command entry and its description to ``target``."""
        signs = [self.prefix, '<', '>', ':', '|']
        marked = f'{self.prefix}{command}'
        for sign in signs:
            marked = marked.replace(sign, f'§6{sign}§f')

        tellraw_json = hover_and_suggest(
            marked,
            suggest=f'{self.prefix}{command}',
            hover=marked,
        )
        self.execute(f'tellraw {target} {tellraw_json}')
        self.send_response(target, f'  ↳ {description}')

    async def get_data(self, player: str, data: str) -> str | None:
        """Query entity NBT ``data`` for ``player`` via RCON."""
        if self.rcon_port is None:
            return None

        try:
            reply = await rcon_execute(
                '127.0.0.1',
                self.rcon_port,
                self.rcon_password,
                f'data get entity {player} {data}',
            )
        except (OSError, TimeoutError, RconError):
            return None

        marker = ' has the following entity data: '
        if marker in reply:
            return reply.split(marker, 1)[1].strip()
        return None
