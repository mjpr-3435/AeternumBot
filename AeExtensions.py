from __future__ import annotations

import asyncio
import contextlib
import importlib
import os
import shutil
import sys
from pathlib import Path
from typing import Any

import discord
from Classes.AeServer import AeServer
from Classes.config import AeternumConfig, load_aeternum_config
from dismanager.classes import BaseAddon, DisManagerClient, ManagedProcess

_COG_DIRS = ('Commands', 'ContextMenus', 'Behaviours')
_BANNER_CREATORS = (
    ('MembersInfo', 'members_extras', 'members_creator'),
    ('Public', 'public_extras', 'public_creator'),
    ('InterviewersInfo', 'interviewers_extras', 'interviewers_creator'),
)


class addon(BaseAddon):
    """Root DisManager addon coordinating AeServer instances, plugins, cogs, guides, and banners."""

    client: DisManagerClient
    addons_root: Path
    persistent_tasks: list[asyncio.Task[Any]]
    loaded_extensions: list[str]
    servers: dict[str, AeServer]
    config: AeternumConfig

    def __init__(self, client: DisManagerClient) -> None:
        self.client            = client
        self.addons_root       = Path(__file__).resolve().parent
        self.persistent_tasks  = []
        self.loaded_extensions = []
        self.servers           = {}

        addons_str = str(self.addons_root)
        if addons_str not in sys.path:
            sys.path.insert(0, addons_str)

        self.config            = load_aeternum_config(self.addons_root / 'config.yml')
        self.client.ae_config  = self.config  # type: ignore[attr-defined]

    # --- Internal Behaviour ---

    def _reload_internal_modules(self) -> None:
        prefixes = ('Utils.', 'Classes.', 'Banners.')
        modules = [name for name in sys.modules if name.startswith(prefixes)]
        for mod_name in modules:
            module = sys.modules.get(mod_name)
            if module is None:
                continue
            try:
                importlib.reload(module)
            except Exception:
                sys.modules.pop(mod_name, None)

    def _init_servers(self) -> None:
        self.servers.clear()
        server_names = {name.casefold() for name in self.config.servers}
        for process in self.client.processes:
            key = process.name.casefold()
            if key not in server_names:
                continue
            self.servers[key] = AeServer(process, self.config)
        self.client.ae_servers = self.servers  # type: ignore[attr-defined]

    def _ensure_player_snapshot(self) -> None:
        snapshot = {
            name: (list(server.online_players), list(server.bots))
            for name, server in self.servers.items()
            if server.is_running()
        }
        if snapshot:
            self.client.__dict__['_ae_player_snapshot'] = snapshot

    def _restore_player_snapshot(self) -> None:
        snapshot: dict[str, tuple[list[str], list[str]]] = self.client.__dict__.pop(
            '_ae_player_snapshot', {}
        )
        for key, (players, bots) in snapshot.items():
            server = self.servers.get(key)
            if server is not None and server.is_running():
                server.online_players = list(players)
                server.bots = list(bots)

    async def _manage_plugins(self) -> None:
        plugins_source = self.addons_root / 'Plugins'
        if not plugins_source.is_dir():
            return

        available = {path.name for path in plugins_source.iterdir() if path.is_file()}

        for process in self.client.processes:
            wanted = self.config.plugins.get(process.name)
            if wanted is None:
                continue

            dest_dir = process.path / '.plugins'
            dest_dir.mkdir(parents=True, exist_ok=True)
            for existing in dest_dir.iterdir():
                if existing.is_file():
                    existing.unlink()

            for plugin_name in wanted:
                if plugin_name not in available:
                    continue
                shutil.copy2(plugins_source / plugin_name, dest_dir / plugin_name)

            await process.reload_plugins()

    def _manage_guides(self) -> None:
        source_dir = self.addons_root / 'Guides'

        guide_count = sum(
            1
            for _root, _dirs, files in os.walk(source_dir)
            for filename in files
            if filename.lower().endswith('.md')
        )

        for process in self.client.processes:
            if process.name not in self.config.guide_targets:
                continue

            dest_dir = process.path / 'server' / 'world' / 'data' / 'aeternum_guides'
            dest_dir.parent.mkdir(parents=True, exist_ok=True)
            if dest_dir.is_dir():
                shutil.rmtree(dest_dir)
            shutil.copytree(source_dir, dest_dir)

            if process.is_running():
                process.execute('guide reload')

            print(f'     -> Guías sincronizadas: {process.name} ({guide_count})')

    async def _load_cogs(self) -> None:
        for cog_dir_name in _COG_DIRS:
            cog_dir = self.addons_root / cog_dir_name
            if not cog_dir.is_dir():
                continue

            for script in sorted(cog_dir.glob('*.py')):
                if script.name.startswith('_'):
                    continue
                extension = f'{cog_dir_name}.{script.stem}'
                if extension in self.client.extensions:
                    await self.client.unload_extension(extension)
                await self.client.load_extension(extension)
                if extension not in self.loaded_extensions:
                    self.loaded_extensions.append(extension)

    def _start_banners(self) -> None:
        banners_dir = self.addons_root / 'Banners'
        if not banners_dir.is_dir():
            return

        for pkg, extras_name, creator_name in _BANNER_CREATORS:
            if not (banners_dir / pkg / 'Creator.py').is_file():
                continue
            mod = importlib.import_module(f'Banners.{pkg}.Creator')
            extras_fn = getattr(mod, extras_name)
            creator_fn = getattr(mod, creator_name)
            self.persistent_tasks.append(asyncio.create_task(extras_fn(self.client)))
            self.persistent_tasks.append(asyncio.create_task(creator_fn(self.client)))

    async def _sync_command_tree(self) -> None:
        try:
            await asyncio.sleep(0.5)
            await self.client.tree.sync()
        except asyncio.CancelledError:
            return
        except Exception as exc:
            print(f'     -> No se pudo sincronizar el árbol de comandos: {exc}')

    # --- DisManager Hooks ---

    async def on_addons_load(self) -> None:
        """Reload config, initialize AeServer instances, sync plugins/guides, load cogs, and start banners."""
        self._reload_internal_modules()
        self.config = load_aeternum_config(self.addons_root / 'config.yml')
        self.client.ae_config = self.config  # type: ignore[attr-defined]
        self._init_servers()
        self._restore_player_snapshot()
        await self._manage_plugins()
        self._manage_guides()
        await self._load_cogs()
        self._start_banners()
        self.persistent_tasks.append(asyncio.create_task(self._sync_command_tree()))

        await self.client.change_presence(
            activity=discord.CustomActivity(name='Aeternum SMP'),
            status=discord.Status.online,
        )

    async def on_addons_unload(self) -> None:
        """Cancel persistent banner tasks and unload extensions before addon reload/shutdown."""
        for task in self.persistent_tasks:
            task.cancel()
        for task in self.persistent_tasks:
            with contextlib.suppress(asyncio.CancelledError):
                await task
        self.persistent_tasks.clear()

        for extension in reversed(self.loaded_extensions):
            if extension in self.client.extensions:
                with contextlib.suppress(Exception):
                    await self.client.unload_extension(extension)
        self.loaded_extensions.clear()

        for extension in [ext for ext in self.client.extensions if ext.startswith('Banners.')]:
            with contextlib.suppress(Exception):
                await self.client.unload_extension(extension)

        self._ensure_player_snapshot()
        self.servers.clear()
        for attr in ('ae_config', 'ae_servers'):
            self.client.__dict__.pop(attr, None)

    async def on_process_log(self, process: ManagedProcess, log: str) -> None:
        """Forward filtered console output from ``process`` to its ``AeServer`` parser."""
        server = self.get_server(process)
        if server is not None:
            await server.on_log(log)

    # --- Public API ---

    def get_server(self, process_or_name: ManagedProcess | str) -> AeServer | None:
        """Return the active ``AeServer`` wrapper for ``process_or_name``."""
        name = process_or_name if isinstance(process_or_name, str) else process_or_name.name
        return self.servers.get(name.casefold())