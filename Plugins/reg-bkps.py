from __future__ import annotations

import asyncio
import json
import os
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

from Classes.AeServer import AeServer
from Classes.config import get_ae_servers
from dismanager.classes import BasePlugin, ManagedProcess
from dismanager.core.managed_process import BackupEntry
from Utils.minecraft_text import extras, hover, hover_and_suggest

_DIMS = ('overworld', 'the_nether', 'the_end')


def _dim_folders(dim: str) -> tuple[str, str, str]:
    if dim == 'overworld':
        return ('entities', 'region', 'poi')
    if dim == 'the_nether':
        return (
            str(Path('DIM-1') / 'entities'),
            str(Path('DIM-1') / 'region'),
            str(Path('DIM-1') / 'poi'),
        )
    if dim == 'the_end':
        return (
            str(Path('DIM1') / 'entities'),
            str(Path('DIM1') / 'region'),
            str(Path('DIM1') / 'poi'),
        )
    raise ValueError(f'Dimensión desconocida: {dim}')


class plugin(BasePlugin):
    """Per-region zip backup, partial md-bkp restore, and whitelist manager."""

    process: ManagedProcess
    server: AeServer
    files_to_zip: dict[str, dict[str, list[str]]]
    creating_bkp: bool
    waiting: bool
    scheduled_backup: dict[str, str]
    scheduled_backup_md: dict[str, BackupEntry]
    player_positions: dict[str, dict[str, dict[str, tuple[float, float, float] | None]]]
    load_confirmed: bool
    loading_bkp: bool
    reg_bkps_dir: Path
    whitelist_text_path: Path
    whitelisted_players: set[str]

    def __init__(self, process: ManagedProcess) -> None:
        self.process = process
        self.server = get_ae_servers(process.client)[process.name.casefold()]
        self.files_to_zip = {}
        self.creating_bkp = False
        self.waiting = False
        self.scheduled_backup = {}
        self.scheduled_backup_md = {}
        self.player_positions = {}
        self.load_confirmed = False
        self.loading_bkp = False

        self.reg_bkps_dir = self.process.plugins_dir / 'reg-bkps'
        self.reg_bkps_dir.mkdir(parents=True, exist_ok=True)
        self.whitelist_text_path = self.reg_bkps_dir / 'whitelist.txt'
        if not self.whitelist_text_path.exists():
            self.whitelist_text_path.write_text('', encoding='utf-8')
        self.whitelisted_players = self._load_whitelist()

    async def on_process_log(self, log: str) -> None:
        if 'INFO]:' in log and log.endswith('Saved the game') and self.waiting:
            self.waiting = False

    async def on_mc_player_command(self, player: str, message: str) -> None:
        self.files_to_zip.setdefault(player, {dim: [] for dim in _DIMS})
        self.player_positions.setdefault(player, {dim: {'pos1': None, 'pos2': None} for dim in _DIMS})
        zips = [path.name for path in self.reg_bkps_dir.glob('*.zip')]

        if self.server.is_command(message, 'mdhelp'):
            self.server.show_command(player, 'rb help', 'Muestra los comandos del regional backup.')
            return

        if self.server.is_command(message, 'rb help'):
            self._show_help(player)
            return

        if self.server.is_command(message, 'rb add'):
            pos_dim = await self._get_player_position(player)
            if pos_dim is None:
                return
            pos, dim = pos_dim
            reg = self._pos_to_region(pos)
            if reg not in self.files_to_zip[player][dim]:
                self.files_to_zip[player][dim].append(reg)
            self._show_list(player)
            return

        if self.server.is_command(message, 'rb remove'):
            pos_dim = await self._get_player_position(player)
            if pos_dim is None:
                return
            pos, dim = pos_dim
            current_reg = self._pos_to_region(pos)
            if current_reg in self.files_to_zip[player][dim]:
                self.files_to_zip[player][dim].remove(current_reg)
                self.server.send_response(player, f'✔ Región {current_reg} eliminada de tu lista.')
            else:
                self.server.send_response(player, '✖ La región actual no está en tu lista.')
            self._show_list(player)
            return

        if self.server.is_command(message, 'rb del'):
            raw_index = message.removeprefix(f'{self.server.prefix}rb del').strip()
            try:
                index = int(raw_index)
            except ValueError:
                self.server.send_response(player, '✖ El índice debe ser un número.')
                return
            if not self._has_regions_selected(player):
                self.server.send_response(player, 'Lista vacía.')
                return
            i = 0
            removed = False
            for dim in _DIMS:
                for reg in list(self.files_to_zip[player][dim]):
                    i += 1
                    if index == i:
                        self.files_to_zip[player][dim].remove(reg)
                        removed = True
            if not removed:
                self.server.send_response(player, '✖ Índice fuera de rango.')
                return
            self._show_list(player)
            return

        if self.server.is_command(message, 'rb list'):
            self._show_list(player)
            return

        if self.server.is_command(message, 'rb bkps'):
            self._show_bkps(player)
            return

        if self.server.is_command(message, 'rb clear'):
            self.files_to_zip[player] = {dim: [] for dim in _DIMS}
            self.player_positions[player] = {dim: {'pos1': None, 'pos2': None} for dim in _DIMS}
            self._show_list(player)
            return

        if self.server.is_command(message, 'rb pos1'):
            await self._set_corner(player, 'pos1', 'pos2')
            return

        if self.server.is_command(message, 'rb pos2'):
            await self._set_corner(player, 'pos2', 'pos1')
            return

        if self.server.is_command(message, 'rb mk-bkp'):
            name = message.removeprefix(f'{self.server.prefix}rb mk-bkp').strip()
            if not self._has_regions_selected(player):
                self.server.send_response(player, '✖ No has agregado ninguna región.')
                return
            if not self._is_safe_name(name):
                self.server.send_response(player, '✖ Nombre de backup inválido.')
                return
            if self.creating_bkp:
                self.server.send_response(player, '✖ Alguien más está creando un backup ahorita.')
                return
            self.creating_bkp = True
            await self._make_reg_bkp(player, name)
            return

        if self.server.is_command(message, 'rb update'):
            name = message.removeprefix(f'{self.server.prefix}rb update').strip()
            if not self._is_safe_name(name) or f'{name}.zip' not in zips:
                self.server.send_response(player, '✖ Debes proveer un nombre válido en la lista.')
                return
            zip_path = self.reg_bkps_dir / f'{name}.zip'

            author = self._read_zip_author(zip_path)
            if not self._is_admin_or_whitelisted(player):
                if author is None:
                    self.server.send_response(player, '✖ No se puede actualizar: backup sin autor registrado.')
                    return
                if player != author:
                    self.server.send_response(
                        player,
                        '✖ Solo los administradores o el creador del backup puede actualizarlo.',
                    )
                    return

            if self.creating_bkp:
                self.server.send_response(player, '✖ Alguien más está creando un backup ahorita.')
                return
            self.creating_bkp = True
            await self._update_reg_bkp(player, name)
            return

        if not self._is_admin_or_whitelisted(player) and self.server.name == 'SMP':
            return

        if self.server.is_command(message, 'rb load-md'):
            await self._handle_load_md(player, message)
            return

        if self.server.is_command(message, 'rb load-bkp'):
            raw_name = message.removeprefix(f'{self.server.prefix}rb load-bkp').strip()
            zip_name = raw_name + '.zip'
            if not self._is_safe_name(raw_name) or zip_name not in zips:
                self.server.send_response(player, '✖ No hay un reg-bkp con ese nombre.')
                return

            self.scheduled_backup[player] = zip_name
            cmd = f'{self.server.prefix}rb confirm'
            tellraw_json = extras(
                [hover_and_suggest(cmd, color='dark_gray', suggest=cmd, hover=cmd)],
                text=f'Para confirmar la carga de §d[{zip_name}]§7 utiliza ',
            )
            self.server.execute(f'tellraw {player} {tellraw_json}')
            return

        if self.server.is_command(message, 'rb confirm'):
            if player not in self.scheduled_backup:
                self.server.send_response(player, '✖ No has solicitado la carga de ningún backup.')
                return
            if self.load_confirmed or self.loading_bkp:
                self.server.send_response(player, '✖ Ya alguien más confirmo la carga de un backup.')
                return

            self.load_confirmed = True
            self.loading_bkp = True
            for i in range(5):
                await asyncio.sleep(1)
                self.server.send_response('@a', f'El servidor se reiniciará en {5 - i} segundos.')
            await self._load_reg_bkp(player)
            return

        if self.server.is_command(message, 'rb confirm-md'):
            await self._handle_confirm_md(player)
            return

        if self.server.is_command(message, 'rb del-bkp'):
            raw_name = message.removeprefix(f'{self.server.prefix}rb del-bkp').strip()
            zip_name = raw_name + '.zip'
            if not self._is_safe_name(raw_name):
                self.server.send_response(player, '✖ Nombre de backup inválido.')
                return
            zip_path = self.reg_bkps_dir / zip_name
            if not zip_path.is_file():
                self.server.send_response(player, '✖ No hay un reg-bkp con ese nombre.')
                return

            author = self._read_zip_author(zip_path)
            if not self._is_admin_or_whitelisted(player):
                if author is None:
                    self.server.send_response(player, '✖ No se puede eliminar: backup sin autor registrado.')
                    return
                if player != author:
                    self.server.send_response(
                        player,
                        '✖ Solo el creador o un admin puede eliminar este backup.',
                    )
                    return

            zip_path.unlink()
            self._show_bkps(player)
            self.server.send_response(player, f'✔ reg-bkp {zip_name} eliminado.')
            return

        if player not in self.server.admins or self.server.name != 'SMP':
            return

        if self.server.is_command(message, 'rb wl list'):
            self._show_whitelist(player)
        elif self.server.is_command(message, 'rb wl add'):
            target = message.removeprefix(f'{self.server.prefix}rb wl add').strip()
            if not target:
                self.server.send_response(player, '✖ Debes proveer un jugador.')
                return
            self.whitelisted_players.add(target)
            self._save_whitelist()
            self.server.send_response(player, f'✔ {target} agregado a la whitelist.')
            self._show_whitelist(player)
        elif self.server.is_command(message, 'rb wl remove'):
            target = message.removeprefix(f'{self.server.prefix}rb wl remove').strip()
            if not target:
                self.server.send_response(player, '✖ Debes proveer un jugador.')
                return
            if target in self.whitelisted_players:
                self.whitelisted_players.remove(target)
                self._save_whitelist()
                self.server.send_response(player, f'✔ {target} removido de la whitelist.')
            else:
                self.server.send_response(player, f'✖ {target} no está en la whitelist.')
            self._show_whitelist(player)
        elif self.server.is_command(message, 'rb wl clear'):
            self.whitelisted_players.clear()
            self._save_whitelist()
            self.server.send_response(player, '✔ Whitelist limpiada.')

    def _show_help(self, player: str) -> None:
        self.server.show_command(player, 'rb clear', 'Limpia tu lista.')
        self.server.show_command(player, 'rb list', 'Muestra tu lista de regiones.')
        self.server.show_command(player, 'rb add', 'Añade a tu lista una región.')
        self.server.show_command(player, 'rb remove', 'Quita de tu lista la región donde te encuentras actualmente.')
        self.server.show_command(player, 'rb pos1', 'Establece la primera esquina de un rectángulo de regiones.')
        self.server.show_command(player, 'rb pos2', 'Establece la segunda esquina de un rectángulo de regions.')
        self.server.show_command(player, 'rb del <index>', 'Elimina la región de índice <index> de tu lista.')
        self.server.show_command(player, 'rb mk-bkp <name>', 'Crea un reg-bkp <name>.zip con las regiones añadidas.')
        self.server.show_command(player, 'rb update <name>', 'Actualiza el reg-bkp <name>.zip reimportando regiones.')
        self.server.show_command(player, 'rb bkps', 'Lista los backups creados.')

        if not self._is_admin_or_whitelisted(player) and self.server.name == 'SMP':
            return
        self.server.show_command(player, 'rb load-bkp <name>', 'Carga el reg-bkp <name>.zip.')
        self.server.show_command(player, 'rb load-md', 'Lista los md-bkps disponibles.')
        self.server.show_command(player, 'rb load-md <name>', 'Carga regiones desde el md-bkp <name>.')
        self.server.show_command(player, 'rb del-bkp <name>', 'Elimina el reg-bkp <name>.zip.')
        self.server.show_command(player, 'rb confirm-md', 'Confirma la carga del md-bkp especificado.')
        self.server.show_command(player, 'rb confirm', 'Confirma la carga del reg-bkp específicado.')

        if player in self.server.admins:
            self.server.show_command(player, 'rb wl list', 'Muestra la whitelist de carga de reg-bkps.')
            self.server.show_command(player, 'rb wl add <player>', 'Añade un jugador a la whitelist.')
            self.server.show_command(player, 'rb wl remove <player>', 'Quita un jugador de la whitelist.')
            self.server.show_command(player, 'rb wl clear', 'Limpia toda la whitelist.')

    async def _handle_load_md(self, player: str, message: str) -> None:
        if not self._has_md_bkps():
            self.server.send_response(player, 'x md-bkps no esta cargado.')
            return

        backup_name = message.removeprefix(f'{self.server.prefix}rb load-md').strip()
        backups = {entry.name: entry for entry in self._get_md_bkps()}

        if not backup_name:
            if not backups:
                self.server.send_response(player, 'No hay md-bkps disponibles.')
                return
            self.server.send_response(player, 'Md-bkps disponibles:')
            for entry in sorted(backups.values(), key=lambda item: item.name):
                creation_time = datetime.fromtimestamp(entry.path.stat().st_ctime)
                cmd = f'{self.server.prefix}rb load-md {entry.name}'
                components = [
                    hover_and_suggest('[>] ', color='green', suggest=cmd, hover='Load regions from md-bkp'),
                    json.dumps({'text': f'{entry.name} [{creation_time.strftime("%Y-%m-%d %H:%M:%S")}]'}),
                ]
                self.server.execute(f'tellraw {player} {extras(components)}')
            return

        if not self._has_regions_selected(player):
            self.server.send_response(player, 'x No has agregado ninguna region.')
            return

        selected = backups.get(backup_name)
        if selected is None:
            self.server.send_response(player, 'x No hay un md-bkp con ese nombre.')
            return

        self.scheduled_backup_md[player] = selected
        cmd = f'{self.server.prefix}rb confirm-md'
        tellraw_json = extras(
            [hover_and_suggest(cmd, color='dark_gray', suggest=cmd, hover=cmd)],
            text=f'Para confirmar la carga desde el md-bkp §d[{backup_name}]§7 utiliza ',
        )
        self.server.execute(f'tellraw {player} {tellraw_json}')

    async def _handle_confirm_md(self, player: str) -> None:
        if not self._has_md_bkps():
            self.server.send_response(player, 'x md-bkps no esta cargado.')
            return
        if player not in self.scheduled_backup_md:
            self.server.send_response(player, 'x No has solicitado la carga de ningun md-bkp.')
            return
        if not self._has_regions_selected(player):
            self.server.send_response(player, 'x No has agregado ninguna region.')
            return

        entry = self.scheduled_backup_md[player]
        if not entry.path.is_dir():
            self.server.send_response(player, 'x No hay un md-bkp con ese nombre.')
            self.scheduled_backup_md.pop(player, None)
            return
        if self.load_confirmed or self.loading_bkp:
            self.server.send_response(player, 'x Ya alguien mas confirmo la carga de un backup.')
            return

        self.load_confirmed = True
        self.loading_bkp = True
        for i in range(5):
            await asyncio.sleep(1)
            self.server.send_response('@a', f'El servidor se reiniciara en {5 - i} segundos.')
        await self._load_md_partial_bkp(player)

    async def _load_reg_bkp(self, player: str) -> None:
        zip_name = self.scheduled_backup.pop(player)
        try:
            self.process.stop()
            while self.process.is_running():
                await asyncio.sleep(0.1)

            discord_message = await self.process.send_to_console(f'[reg-bkps]: Unpacking reg-bkp {zip_name}...')
            source = self.reg_bkps_dir / zip_name
            destination = self.process.path / 'server' / 'world'

            with zipfile.ZipFile(source, 'r') as zip_ref:
                for file in zip_ref.namelist():
                    zip_ref.extract(file, destination)

            (destination / 'bkp_log.txt').unlink(missing_ok=True)
            if discord_message is not None:
                await discord_message.edit(content=f'```md\n[reg-bkps]: ✔ Reg-bkp {zip_name} unpacked.```')

            self.process.start()
        finally:
            self.load_confirmed = False
            self.loading_bkp = False

    async def _load_md_partial_bkp(self, player: str) -> None:
        entry = self.scheduled_backup_md.pop(player)
        self.process.stop()
        while self.process.is_running():
            await asyncio.sleep(0.1)

        discord_message = await self.process.send_to_console(
            f'[reg-bkps]: Loading regions from md-bkp {entry.name}...'
        )
        self.server.send_response('@a', '[reg-bkps]: Loading regions from md-bkp...')

        destination = self.process.path / 'server' / 'world'
        copied_files = 0
        try:
            for dim in _DIMS:
                folders = _dim_folders(dim)
                for reg in self.files_to_zip[player][dim]:
                    for folder in folders:
                        source_file = entry.path / 'server' / 'world' / folder / reg
                        if not source_file.is_file():
                            continue
                        dest_file = destination / folder / reg
                        dest_file.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(source_file, dest_file)
                        copied_files += 1

            if discord_message is not None:
                await discord_message.edit(
                    content=f'```md\n[reg-bkps]: OK Loaded {copied_files} region files from md-bkp {entry.name}.```'
                )
            self.server.send_response('@a', f'[reg-bkps]: {copied_files} archivos copiados desde md-bkp.')
        except Exception:
            if discord_message is not None:
                await discord_message.edit(
                    content=f'```md\n[reg-bkps]: x Error loading regions from md-bkp {entry.name}.```'
                )
            raise
        finally:
            self.load_confirmed = False
            self.loading_bkp = False
            self.process.start()

    async def _make_reg_bkp(self, player: str, name: str) -> None:
        destination = self.reg_bkps_dir / f'{name}.zip'
        destination.parent.mkdir(parents=True, exist_ok=True)

        self.waiting = True
        self.process.execute('save-off')
        self.process.execute('save-all')
        try:
            while self.waiting:
                await asyncio.sleep(1)

            self.server.send_response(player, f'Creando {name}.zip...')
            self._write_region_zip(destination, player)
            self.server.send_response(player, f'✔ reg-bkp {name}.zip creado.')
            self.process.add_log(f'reg-bkp {name}.zip created')
        finally:
            self.process.execute('save-on')
            self.creating_bkp = False
            self.waiting = False

    async def _update_reg_bkp(self, player: str, name: str) -> None:
        zip_path = self.reg_bkps_dir / f'{name}.zip'
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                if 'bkp_log.txt' not in zip_ref.namelist():
                    self.server.send_response(
                        player,
                        f'✖ El reg-bkp {name}.zip no tiene registro de regiones.',
                    )
                    return
                raw_lines = zip_ref.read('bkp_log.txt').decode('utf-8', errors='replace').splitlines()

            self.files_to_zip[player] = {dim: [] for dim in _DIMS}
            for line in raw_lines:
                if ' : r.' in line and line.endswith('.mca'):
                    dim, region = (part.strip() for part in line.split(':', 1))
                    if dim in self.files_to_zip[player]:
                        self.files_to_zip[player][dim].append(region)

            self.waiting = True
            self.process.execute('save-off')
            self.process.execute('save-all')
            while self.waiting:
                await asyncio.sleep(1)

            self.server.send_response(player, f'Creando {name}.zip...')
            self._write_region_zip(zip_path, player)
            self.server.send_response(player, f'✔ reg-bkp {name}.zip actualizado.')
            self.process.add_log(f'reg-bkp {name}.zip updated')
        finally:
            self.process.execute('save-on')
            self.creating_bkp = False
            self.waiting = False

    def _write_region_zip(self, destination: Path, player: str) -> None:
        log_content: list[str] = []
        with zipfile.ZipFile(destination, 'w') as zipf:
            for dim in _DIMS:
                folders = _dim_folders(dim)
                for reg in self.files_to_zip[player][dim]:
                    for folder in folders:
                        file_path = self.process.path / 'server' / 'world' / folder / reg
                        if file_path.is_file():
                            zipf.write(file_path, os.path.join(folder, reg))
                    log_content.append(f'{dim} : {reg}')

            log_text = f'Backup realizado por: {player}\nArchivos respaldados:\n' + '\n'.join(log_content)
            zipf.writestr('bkp_log.txt', log_text)

    @staticmethod
    def _read_zip_author(zip_path: Path) -> str | None:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            if 'bkp_log.txt' not in zip_ref.namelist():
                return None
            lines = zip_ref.read('bkp_log.txt').decode('utf-8', errors='replace').splitlines()
        if lines and lines[0].startswith('Backup realizado por:'):
            return lines[0].removeprefix('Backup realizado por:').strip()
        return None

    @staticmethod
    def _is_safe_name(name: str) -> bool:
        return bool(name) and '/' not in name and '\\' not in name and '..' not in name

    async def _set_corner(self, player: str, corner: str, other: str) -> None:
        pos_dim = await self._get_player_position(player)
        if pos_dim is None:
            return
        pos, dim = pos_dim
        self.player_positions[player][dim][corner] = pos
        self.server.send_response(player, f'✔ {corner.capitalize()} establecida')
        if self.player_positions[player][dim][other] is not None:
            self._add_rect_regions(player, dim)
            self._show_list(player)

    def _is_admin_or_whitelisted(self, player: str) -> bool:
        return player in self.server.admins or player in self.whitelisted_players

    def _show_whitelist(self, player: str) -> None:
        if not self.whitelisted_players:
            self.server.send_response(player, 'Whitelist vacía.')
            return
        lines = ['Whitelist de reg-bkps:']
        for i, whitelisted in enumerate(sorted(self.whitelisted_players), start=1):
            lines.append(f'{i} • {whitelisted}')
        self.server.send_response(player, lines)

    def _load_whitelist(self) -> set[str]:
        players = self.whitelist_text_path.read_text(encoding='utf-8').strip().splitlines()
        return {player for player in players if player}

    def _save_whitelist(self) -> None:
        self.whitelist_text_path.write_text(
            '\n'.join(sorted(self.whitelisted_players)),
            encoding='utf-8',
        )

    def _has_md_bkps(self) -> bool:
        return (self.process.plugins_dir / 'md-bkps.py').is_file() and self.process.backups_dir.is_dir()

    def _get_md_bkps(self) -> list[BackupEntry]:
        if not self._has_md_bkps():
            return []
        return sorted(self.process.list_backups(), key=lambda entry: entry.name)

    def _has_regions_selected(self, player: str) -> bool:
        return any(self.files_to_zip[player][dim] for dim in _DIMS)

    def _show_list(self, player: str) -> None:
        if player not in self.files_to_zip:
            self.server.send_response(player, 'Lista vacía.')
            return

        lines: list[str] = []
        i = 0
        for dim in _DIMS:
            for reg in self.files_to_zip[player][dim]:
                i += 1
                lines.append(f'{i} • {dim} : {reg}')

        if lines:
            lines.insert(0, f'{player}, region list:')
            self.server.send_response(player, lines)
        else:
            self.server.send_response(player, 'Lista vacía.')

    def _show_bkps(self, player: str) -> None:
        zips = sorted(self.reg_bkps_dir.glob('*.zip'), key=lambda path: path.name)
        if not zips:
            self.server.send_response(player, 'No se han creado backups.')
            return

        self.server.send_response(player, 'Reg-bkps disponibles:')
        now = datetime.now()

        for zip_path in zips:
            creation_time = datetime.fromtimestamp(zip_path.stat().st_ctime)
            time_diff = now - creation_time
            if time_diff.days > 0:
                time_ago = f'Hace {time_diff.days} días'
            elif time_diff.seconds >= 3600:
                time_ago = f'Hace {time_diff.seconds // 3600} horas'
            elif time_diff.seconds >= 60:
                time_ago = f'Hace {time_diff.seconds // 60} minutos'
            else:
                time_ago = 'Hace unos segundos'

            log_info = self._format_zip_hover(zip_path)
            stem = zip_path.stem
            components = [
                hover_and_suggest(
                    '[>] ',
                    color='green',
                    suggest=f'{self.server.prefix}rb load-bkp {stem}',
                    hover='Load reg-bkp',
                ),
                hover_and_suggest(
                    '[⥁] ',
                    color='aqua',
                    suggest=f'{self.server.prefix}rb update {stem}',
                    hover='Update reg-bkp',
                ),
                hover_and_suggest(
                    '[x] ',
                    color='red',
                    suggest=f'{self.server.prefix}rb del-bkp {stem}',
                    hover='Del reg-bkp',
                ),
                hover('[ℹ] ', color='yellow', hover=log_info),
                json.dumps({'text': f'{zip_path.name} [{creation_time.strftime("%Y-%m-%d %H:%M:%S")}] [{time_ago}]'}),
            ]
            self.server.execute(f'tellraw {player} {extras(components)}')

    @staticmethod
    def _format_zip_hover(zip_path: Path) -> str:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            if 'bkp_log.txt' not in zip_ref.namelist():
                return 'Sin registro.'
            lines = zip_ref.read('bkp_log.txt').decode('utf-8', errors='replace').splitlines()

        if len(lines) > 2:
            author = lines[0].removeprefix('Backup realizado por: ').strip()
            regions_log = ' | '.join(lines[2:])
            return f'Hecho por: {author} | {regions_log}'
        if len(lines) > 1:
            author = lines[0].removeprefix('Backup realizado por: ').strip()
            return f'Hecho por: {author}'
        return 'Sin registro de autor.'

    @staticmethod
    def _pos_to_region(pos: tuple[float, float, float]) -> str:
        r_x = int(pos[0] // (32 * 16))
        r_z = int(pos[2] // (32 * 16))
        return f'r.{r_x}.{r_z}.mca'

    async def _get_player_position(
        self, player: str
    ) -> tuple[tuple[float, float, float], str] | None:
        raw_pos = await self.server.get_data(player, 'Pos')
        raw_dim = await self.server.get_data(player, 'Dimension')
        if raw_pos is None or raw_dim is None:
            self.server.send_response(player, '✖ No se pudo obtener tu posición vía RCON.')
            return None

        coords = raw_pos[raw_pos.find('[') + 1 : raw_pos.find(']')].split(',')
        pos = (
            float(coords[0].strip()[:-1]),
            float(coords[1].strip()[:-1]),
            float(coords[2].strip()[:-1]),
        )
        dim = raw_dim.replace('"', '').split(':')[1]
        return pos, dim

    def _get_region_folder(self, dim: str) -> Path:
        base = self.process.path / 'server' / 'world'
        if dim == 'overworld':
            return base / 'region'
        if dim == 'the_nether':
            return base / 'DIM-1' / 'region'
        if dim == 'the_end':
            return base / 'DIM1' / 'region'
        raise ValueError(f'Dimensión desconocida: {dim}')

    def _add_rect_regions(self, player: str, dim: str) -> None:
        pos1 = self.player_positions[player][dim]['pos1']
        pos2 = self.player_positions[player][dim]['pos2']
        if pos1 is None or pos2 is None:
            return

        x_min, x_max = sorted([pos1[0], pos2[0]])
        z_min, z_max = sorted([pos1[2], pos2[2]])
        self.files_to_zip[player][dim] = []

        region_folder = self._get_region_folder(dim)
        if not region_folder.is_dir():
            return

        for reg_path in region_folder.glob('*.mca'):
            r_x, r_z = map(int, reg_path.stem[2:].split('.'))
            reg_x_min = r_x * 512
            reg_x_max = reg_x_min + 511
            reg_z_min = r_z * 512
            reg_z_max = reg_z_min + 511
            if not (reg_x_max < x_min or reg_x_min > x_max or reg_z_max < z_min or reg_z_min > z_max):
                self.files_to_zip[player][dim].append(reg_path.name)
