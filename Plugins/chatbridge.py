from __future__ import annotations

import discord
from dismanager.classes import BasePlugin, ManagedProcess

from Classes import AeServer, get_ae_config, get_ae_servers


class plugin(BasePlugin):
    """Bridge in-game chat and server lifecycle events to Discord and sibling servers."""

    process: ManagedProcess
    server: AeServer
    webhook: discord.Webhook | None

    def __init__(self, process: ManagedProcess) -> None:
        self.process = process
        self.server = get_ae_servers(process.client)[process.name.casefold()]
        self.webhook = None

    async def on_plugins_load(self) -> None:
        cb_cfg = get_ae_config(self.process.client).chatbridge
        channel = self.process.client.get_channel(cb_cfg.channel_id)
        if not isinstance(channel, discord.TextChannel):
            return

        webhooks = await channel.webhooks()
        self.webhook = next((wh for wh in webhooks if wh.name == cb_cfg.webhook_name), None)

    async def on_mc_player_message(self, player: str, message: str) -> None:
        if self.webhook is None:
            return
        self._send_to_servers(f'[{self.server.name}] <{player}> {message}')
        await self.webhook.send(
            message,
            username=f'[{self.server.name}] {player}',
            avatar_url=f'https://mc-heads.net/head/{player.lower()}.png',
        )

    async def on_mc_player_join(self, player: str) -> None:
        await self._broadcast(f'[{self.server.name}] {player} ha entrado al servidor')

    async def on_mc_player_left(self, player: str) -> None:
        await self._broadcast(f'[{self.server.name}] {player} ha salido del servidor')

    async def on_mc_ready(self) -> None:
        await self._broadcast(f'[{self.server.name}] Servidor abierto!')

    async def on_mc_stopped(self) -> None:
        await self._broadcast(f'[{self.server.name}] Servidor detenido')

    async def on_mc_crash(self) -> None:
        await self._broadcast(f'[{self.server.name}] El servidor crasheó')

    async def _broadcast(self, text: str) -> None:
        if self.webhook is None:
            return
        self._send_to_servers(text)
        await self.webhook.send(text)

    def _send_to_servers(self, msg: str) -> None:
        sanitized = msg.replace('\n', '').replace('"', "'")
        for other in get_ae_servers(self.process.client).values():
            if other.name != self.server.name and (other.online_players or other.bots):
                other.send_response('@a', sanitized)
