from __future__ import annotations

import asyncio
import json
import math
import os
import shutil
import struct
import zipfile
from datetime import datetime
from pathlib import Path

from Classes.AeServer import AeServer
from Classes.config import get_ae_servers
from dismanager.classes import BasePlugin, ManagedProcess
from dismanager.core.managed_process import BackupEntry
from Utils.minecraft_text import extras, hover, hover_and_suggest

_DIMS = ('overworld', 'the_nether', 'the_end')
_MAX_SELECTED_CHUNKS = 65536  # 256x256 chunks (~4096x4096 bloques)
_SECTOR_BYTES = 4096
_HEADER_BYTES = _SECTOR_BYTES * 2


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


def _chunk_to_region(cx: int, cz: int) -> tuple[str, int]:
    rx = cx // 32
    rz = cz // 32
    index = (cx % 32) + (cz % 32) * 32
    return f'r.{rx}.{rz}.mca', index


def _read_mca_chunks(mca_bytes: bytes) -> tuple[dict[int, tuple[bytes, int]], set[int]]:
    """Return ({index: (raw_chunk_bytes, timestamp)}, external_mcc_indices) from an .mca file."""
    chunks: dict[int, tuple[bytes, int]] = {}
    external_indices: set[int] = set()
    if len(mca_bytes) < _HEADER_BYTES:
        return chunks, external_indices

    for index in range(1024):
        loc_val = struct.unpack_from('>I', mca_bytes, index * 4)[0]
        offset = (loc_val >> 8) & 0xFFFFFF
        sector_count = loc_val & 0xFF
        if offset < 2 or sector_count == 0:
            continue

        byte_offset = offset * _SECTOR_BYTES
        if byte_offset + 5 > len(mca_bytes):
            continue

        payload_len = struct.unpack_from('>I', mca_bytes, byte_offset)[0]
        compression_type = mca_bytes[byte_offset + 4]
        total_len = 4 + payload_len
        if payload_len == 0 or byte_offset + total_len > len(mca_bytes):
            continue

        timestamp = struct.unpack_from('>I', mca_bytes, _SECTOR_BYTES + index * 4)[0]
        chunks[index] = (mca_bytes[byte_offset : byte_offset + total_len], timestamp)
        if compression_type & 0x80:
            external_indices.add(index)

    return chunks, external_indices


def _pack_mca_chunks(chunks: dict[int, tuple[bytes, int]]) -> bytes:
    """Pack {index: (raw_chunk_bytes, timestamp)} into valid .mca bytes."""
    locations = bytearray(_SECTOR_BYTES)
    timestamps = bytearray(_SECTOR_BYTES)
    body = bytearray()
    current_sector = 2

    for index in sorted(chunks):
        raw_bytes, ts = chunks[index]
        sector_count = max(1, math.ceil(len(raw_bytes) / _SECTOR_BYTES))
        padded_len = sector_count * _SECTOR_BYTES

        struct.pack_into('>I', locations, index * 4, (current_sector << 8) | sector_count)
        struct.pack_into('>I', timestamps, index * 4, ts)

        body.extend(raw_bytes)
        if len(raw_bytes) < padded_len:
            body.extend(b'\x00' * (padded_len - len(raw_bytes)))
        current_sector += sector_count

    return bytes(locations) + bytes(timestamps) + bytes(body)


def _extract_chunks_from_mca(mca_bytes: bytes, indices: set[int]) -> tuple[bytes | None, set[int]]:
    """Extract only the specified chunk indices from an .mca file."""
    all_chunks, external = _read_mca_chunks(mca_bytes)
    filtered = {idx: data for idx, data in all_chunks.items() if idx in indices}
    if not filtered:
        return None, set()
    return _pack_mca_chunks(filtered), external & set(filtered)


def _merge_chunks_into_mca(
    world_mca_bytes: bytes | None,
    source_mca_bytes: bytes | None,
    target_indices: set[int],
) -> tuple[bytes | None, set[int]]:
    """Merge target_indices from source_mca_bytes into world_mca_bytes, clearing missing target_indices."""
    world_chunks: dict[int, tuple[bytes, int]] = {}
    if world_mca_bytes is not None:
        world_chunks, _ = _read_mca_chunks(world_mca_bytes)

    source_chunks: dict[int, tuple[bytes, int]] = {}
    source_external: set[int] = set()
    if source_mca_bytes is not None:
        source_chunks, source_external = _read_mca_chunks(source_mca_bytes)

    for idx in target_indices:
        if idx in source_chunks:
            world_chunks[idx] = source_chunks[idx]
        else:
            world_chunks.pop(idx, None)

    if not world_chunks:
        return None, set()
    return _pack_mca_chunks(world_chunks), source_external & target_indices


class plugin(BasePlugin):
    """Per-chunk zip backup and partial md-bkp restore for Minecraft 1.21.6."""

    process: ManagedProcess
    server: AeServer
    files_to_zip: dict[str, dict[str, list[tuple[int, int]]]]
    creating_bkp: bool
    waiting: bool
    scheduled_backup: dict[str, str]
    scheduled_backup_md: dict[str, BackupEntry]
    player_positions: dict[str, dict[str, dict[str, tuple[float, float, float] | None]]]
    load_confirmed: bool
    loading_bkp: bool
    chunk_bkps_dir: Path

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

        self.chunk_bkps_dir = self.process.plugins_dir / 'chunk-bkp'
        self.chunk_bkps_dir.mkdir(parents=True, exist_ok=True)

    async def on_process_log(self, log: str) -> None:
        if 'INFO]:' in log and log.rstrip().endswith('Saved the game') and self.waiting:
            self.waiting = False

    async def on_mc_player_command(self, player: str, message: str) -> None:
        self.files_to_zip.setdefault(player, {dim: [] for dim in _DIMS})
        self.player_positions.setdefault(player, {dim: {'pos1': None, 'pos2': None} for dim in _DIMS})
        zips = [path.name for path in self.chunk_bkps_dir.glob('*.zip')]

        if self.server.is_command(message, 'mdhelp'):
            self.server.show_command(player, 'cb help', 'Muestra los comandos del chunk backup.')
            return

        if self.server.is_command(message, 'cb help'):
            self._show_help(player)
            return

        if self.server.is_command(message, 'cb add'):
            pos_dim = await self._get_player_position(player)
            if pos_dim is None:
                return
            pos, dim = pos_dim
            chunk = self._pos_to_chunk(pos)
            if chunk not in self.files_to_zip[player][dim]:
                total_selected = sum(len(chunks) for chunks in self.files_to_zip[player].values())
                if total_selected >= _MAX_SELECTED_CHUNKS:
                    self.server.send_response(
                        player,
                        f'✖ Límite de {_MAX_SELECTED_CHUNKS:,} chunks alcanzado.',
                    )
                    return
                self.files_to_zip[player][dim].append(chunk)
            self._show_list(player)
            return

        if self.server.is_command(message, 'cb remove'):
            pos_dim = await self._get_player_position(player)
            if pos_dim is None:
                return
            pos, dim = pos_dim
            current_chunk = self._pos_to_chunk(pos)
            if current_chunk in self.files_to_zip[player][dim]:
                self.files_to_zip[player][dim].remove(current_chunk)
                self.server.send_response(
                    player,
                    f'✔ Chunk ({current_chunk[0]}, {current_chunk[1]}) eliminado de tu lista.',
                )
            else:
                self.server.send_response(player, '✖ El chunk actual no está en tu lista.')
            self._show_list(player)
            return

        if self.server.is_command(message, 'cb del'):
            raw_index = message.removeprefix(f'{self.server.prefix}cb del').strip()
            try:
                index = int(raw_index)
            except ValueError:
                self.server.send_response(player, '✖ El índice debe ser un número.')
                return
            if not self._has_chunks_selected(player):
                self.server.send_response(player, 'Lista vacía.')
                return
            i = 0
            removed = False
            for dim in _DIMS:
                for chunk in list(self.files_to_zip[player][dim]):
                    i += 1
                    if index == i:
                        self.files_to_zip[player][dim].remove(chunk)
                        removed = True
            if not removed:
                self.server.send_response(player, '✖ Índice fuera de rango.')
                return
            self._show_list(player)
            return

        if self.server.is_command(message, 'cb list'):
            self._show_list(player)
            return

        if self.server.is_command(message, 'cb bkps'):
            self._show_bkps(player)
            return

        if self.server.is_command(message, 'cb clear'):
            self.files_to_zip[player] = {dim: [] for dim in _DIMS}
            self.player_positions[player] = {dim: {'pos1': None, 'pos2': None} for dim in _DIMS}
            self._show_list(player)
            return

        if self.server.is_command(message, 'cb pos1'):
            await self._set_corner(player, 'pos1', 'pos2')
            return

        if self.server.is_command(message, 'cb pos2'):
            await self._set_corner(player, 'pos2', 'pos1')
            return

        if self.server.is_command(message, 'cb mk-bkp'):
            name = message.removeprefix(f'{self.server.prefix}cb mk-bkp').strip()
            if not self._has_chunks_selected(player):
                self.server.send_response(player, '✖ No has agregado ningún chunk.')
                return
            if not self._is_safe_name(name):
                self.server.send_response(player, '✖ Nombre de backup inválido.')
                return
            if self.creating_bkp:
                self.server.send_response(player, '✖ Alguien más está creando un backup ahorita.')
                return
            self.creating_bkp = True
            await self._make_chunk_bkp(player, name)
            return

        if self.server.is_command(message, 'cb update'):
            name = message.removeprefix(f'{self.server.prefix}cb update').strip()
            if not self._is_safe_name(name) or f'{name}.zip' not in zips:
                self.server.send_response(player, '✖ Debes proveer un nombre válido en la lista.')
                return
            zip_path = self.chunk_bkps_dir / f'{name}.zip'

            author = self._read_zip_author(zip_path)
            if player not in self.server.admins:
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
            await self._update_chunk_bkp(player, name)
            return

        if player not in self.server.admins and self.server.name == 'SMP':
            return

        if self.server.is_command(message, 'cb load-md'):
            await self._handle_load_md(player, message)
            return

        if self.server.is_command(message, 'cb load-bkp'):
            raw_name = message.removeprefix(f'{self.server.prefix}cb load-bkp').strip()
            zip_name = raw_name + '.zip'
            if not self._is_safe_name(raw_name) or zip_name not in zips:
                self.server.send_response(player, '✖ No hay un chunk-bkp con ese nombre.')
                return

            self.scheduled_backup[player] = zip_name
            target_chunks = self._read_zip_chunks(self.chunk_bkps_dir / zip_name)
            self._warn_collisions(player, target_chunks, exclude_name=zip_name)
            cmd = f'{self.server.prefix}cb confirm'
            tellraw_json = extras(
                [hover_and_suggest(cmd, color='dark_gray', suggest=cmd, hover=cmd)],
                text=f'Para confirmar la carga de §d[{zip_name}]§7 utiliza ',
            )
            self.server.execute(f'tellraw {player} {tellraw_json}')
            return

        if self.server.is_command(message, 'cb confirm'):
            if player not in self.scheduled_backup:
                self.server.send_response(player, '✖ No has solicitado la carga de ningún backup.')
                return
            if self.load_confirmed or self.loading_bkp:
                self.server.send_response(player, '✖ Ya alguien más confirmó la carga de un backup.')
                return

            self.load_confirmed = True
            self.loading_bkp = True
            for i in range(5):
                await asyncio.sleep(1)
                self.server.send_response('@a', f'El servidor se reiniciará en {5 - i} segundos.')
            await self._load_chunk_bkp(player)
            return

        if self.server.is_command(message, 'cb confirm-md'):
            await self._handle_confirm_md(player)
            return

        if self.server.is_command(message, 'cb del-bkp'):
            raw_name = message.removeprefix(f'{self.server.prefix}cb del-bkp').strip()
            zip_name = raw_name + '.zip'
            if not self._is_safe_name(raw_name):
                self.server.send_response(player, '✖ Nombre de backup inválido.')
                return
            zip_path = self.chunk_bkps_dir / zip_name
            if not zip_path.is_file():
                self.server.send_response(player, '✖ No hay un chunk-bkp con ese nombre.')
                return

            author = self._read_zip_author(zip_path)
            if player not in self.server.admins:
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
            self.server.send_response(player, f'✔ chunk-bkp {zip_name} eliminado.')
            return

    def _show_help(self, player: str) -> None:
        self.server.show_command(player, 'cb clear', 'Limpia tu lista.')
        self.server.show_command(player, 'cb list', 'Muestra tu lista de chunks.')
        self.server.show_command(player, 'cb add', 'Añade a tu lista el chunk donde te encuentras.')
        self.server.show_command(player, 'cb remove', 'Quita de tu lista el chunk donde te encuentras actualmente.')
        self.server.show_command(player, 'cb pos1', 'Establece la primera esquina de un rectángulo de chunks.')
        self.server.show_command(player, 'cb pos2', 'Establece la segunda esquina de un rectángulo de chunks.')
        self.server.show_command(player, 'cb del <index>', 'Elimina el chunk de índice <index> de tu lista.')
        self.server.show_command(player, 'cb mk-bkp <name>', 'Crea un chunk-bkp <name>.zip con los chunks añadidos.')
        self.server.show_command(player, 'cb update <name>', 'Actualiza el chunk-bkp <name>.zip reimportando chunks.')
        self.server.show_command(player, 'cb bkps', 'Lista los backups creados.')

        if player not in self.server.admins and self.server.name == 'SMP':
            return
        self.server.show_command(player, 'cb load-bkp <name>', 'Carga el chunk-bkp <name>.zip.')
        self.server.show_command(player, 'cb load-md', 'Lista los md-bkps disponibles.')
        self.server.show_command(player, 'cb load-md <name>', 'Carga chunks desde el md-bkp <name>.')
        self.server.show_command(player, 'cb del-bkp <name>', 'Elimina el chunk-bkp <name>.zip.')
        self.server.show_command(player, 'cb confirm-md', 'Confirma la carga del md-bkp especificado.')
        self.server.show_command(player, 'cb confirm', 'Confirma la carga del chunk-bkp especificado.')

    async def _handle_load_md(self, player: str, message: str) -> None:
        if not self._has_md_bkps():
            self.server.send_response(player, '✖ md-bkps no está cargado.')
            return

        backup_name = message.removeprefix(f'{self.server.prefix}cb load-md').strip()
        backups = {entry.name: entry for entry in self._get_md_bkps()}

        if not backup_name:
            if not backups:
                self.server.send_response(player, 'No hay md-bkps disponibles.')
                return
            self.server.send_response(player, 'Md-bkps disponibles:')
            for entry in backups.values():
                date_str = entry.created_at or datetime.fromtimestamp(entry.path.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                cmd = f'{self.server.prefix}cb load-md {entry.name}'
                components = [
                    hover_and_suggest('[>] ', color='green', suggest=cmd, hover='Load chunks from md-bkp'),
                    json.dumps({'text': f'{entry.name} [{date_str}]'}),
                ]
                self.server.execute(f'tellraw {player} {extras(components)}')
            return

        if not self._has_chunks_selected(player):
            self.server.send_response(player, '✖ No has agregado ningún chunk.')
            return

        selected = backups.get(backup_name)
        if selected is None:
            self.server.send_response(player, '✖ No hay un md-bkp con ese nombre.')
            return

        self.scheduled_backup_md[player] = selected
        target_chunks = {
            (dim, chunk)
            for dim in _DIMS
            for chunk in self.files_to_zip[player][dim]
        }
        self._warn_collisions(player, target_chunks)
        cmd = f'{self.server.prefix}cb confirm-md'
        tellraw_json = extras(
            [hover_and_suggest(cmd, color='dark_gray', suggest=cmd, hover=cmd)],
            text=f'Para confirmar la carga desde el md-bkp §d[{backup_name}]§7 utiliza ',
        )
        self.server.execute(f'tellraw {player} {tellraw_json}')

    async def _handle_confirm_md(self, player: str) -> None:
        if not self._has_md_bkps():
            self.server.send_response(player, '✖ md-bkps no está cargado.')
            return
        if player not in self.scheduled_backup_md:
            self.server.send_response(player, '✖ No has solicitado la carga de ningún md-bkp.')
            return
        if not self._has_chunks_selected(player):
            self.server.send_response(player, '✖ No has agregado ningún chunk.')
            return

        entry = self.scheduled_backup_md[player]
        if not entry.path.is_dir():
            self.server.send_response(player, '✖ No hay un md-bkp con ese nombre.')
            self.scheduled_backup_md.pop(player, None)
            return
        if self.load_confirmed or self.loading_bkp:
            self.server.send_response(player, '✖ Ya alguien más confirmó la carga de un backup.')
            return

        self.load_confirmed = True
        self.loading_bkp = True
        for i in range(5):
            await asyncio.sleep(1)
            self.server.send_response('@a', f'El servidor se reiniciará en {5 - i} segundos.')
        await self._load_md_partial_bkp(player)

    async def _load_chunk_bkp(self, player: str) -> None:
        zip_name = self.scheduled_backup.pop(player)
        try:
            self.process.stop()
            while self.process.is_running():
                await asyncio.sleep(0.1)

            discord_message = await self.process.send_to_console(f'[chunk-bkp]: Unpacking chunk-bkp {zip_name}...')
            source = self.chunk_bkps_dir / zip_name
            destination = self.process.path / 'server' / 'world'

            chunks_by_dim = self._read_zip_chunks_by_dim(source)
            with zipfile.ZipFile(source, 'r') as zip_ref:
                zip_names = set(zip_ref.namelist())
                for dim, chunk_list in chunks_by_dim.items():
                    if not chunk_list:
                        continue
                    region_groups = self._group_chunks_by_region(chunk_list)
                    folders = _dim_folders(dim)
                    for reg_name, index_map in region_groups.items():
                        target_indices = set(index_map.keys())
                        for folder in folders:
                            arc_mca = Path(folder, reg_name).as_posix()
                            dest_mca = destination / folder / reg_name

                            source_bytes = zip_ref.read(arc_mca) if arc_mca in zip_names else None
                            world_bytes = dest_mca.read_bytes() if dest_mca.is_file() else None
                            if source_bytes is None and world_bytes is None:
                                continue

                            merged_bytes, ext_indices = _merge_chunks_into_mca(world_bytes, source_bytes, target_indices)
                            if merged_bytes is not None:
                                dest_mca.parent.mkdir(parents=True, exist_ok=True)
                                dest_mca.write_bytes(merged_bytes)
                            elif dest_mca.is_file():
                                dest_mca.unlink()

                            for idx in target_indices:
                                cx, cz = index_map[idx]
                                mcc_name = f'c.{cx}.{cz}.mcc'
                                arc_mcc = Path(folder, mcc_name).as_posix()
                                dest_mcc = destination / folder / mcc_name
                                if idx in ext_indices and arc_mcc in zip_names:
                                    dest_mcc.parent.mkdir(parents=True, exist_ok=True)
                                    dest_mcc.write_bytes(zip_ref.read(arc_mcc))
                                elif dest_mcc.is_file():
                                    dest_mcc.unlink()

            if discord_message is not None:
                await discord_message.edit(content=f'```md\n[chunk-bkp]: ✔ Chunk-bkp {zip_name} unpacked.```')

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
            f'[chunk-bkp]: Loading chunks from md-bkp {entry.name}...'
        )
        self.server.send_response('@a', '[chunk-bkp]: Loading chunks from md-bkp...')

        destination = self.process.path / 'server' / 'world'
        updated_regions = 0
        try:
            for dim in _DIMS:
                chunk_list = self.files_to_zip[player][dim]
                if not chunk_list:
                    continue
                region_groups = self._group_chunks_by_region(chunk_list)
                folders = _dim_folders(dim)
                for reg_name, index_map in region_groups.items():
                    target_indices = set(index_map.keys())
                    for folder in folders:
                        src_mca = entry.path / 'server' / 'world' / folder / reg_name
                        dest_mca = destination / folder / reg_name
                        source_bytes = src_mca.read_bytes() if src_mca.is_file() else None
                        world_bytes = dest_mca.read_bytes() if dest_mca.is_file() else None
                        if source_bytes is None and world_bytes is None:
                            continue

                        merged_bytes, ext_indices = _merge_chunks_into_mca(world_bytes, source_bytes, target_indices)
                        if merged_bytes is not None:
                            dest_mca.parent.mkdir(parents=True, exist_ok=True)
                            dest_mca.write_bytes(merged_bytes)
                            updated_regions += 1
                        elif dest_mca.is_file():
                            dest_mca.unlink()

                        for idx in target_indices:
                            cx, cz = index_map[idx]
                            mcc_name = f'c.{cx}.{cz}.mcc'
                            src_mcc = entry.path / 'server' / 'world' / folder / mcc_name
                            dest_mcc = destination / folder / mcc_name
                            if idx in ext_indices and src_mcc.is_file():
                                dest_mcc.parent.mkdir(parents=True, exist_ok=True)
                                shutil.copy2(src_mcc, dest_mcc)
                            elif dest_mcc.is_file():
                                dest_mcc.unlink()

            if discord_message is not None:
                await discord_message.edit(
                    content=f'```md\n[chunk-bkp]: OK Loaded chunks across {updated_regions} region files from md-bkp {entry.name}.```'
                )
            self.server.send_response('@a', f'[chunk-bkp]: Chunks restaurados en {updated_regions} archivos de región.')
        except Exception:
            if discord_message is not None:
                await discord_message.edit(
                    content=f'```md\n[chunk-bkp]: x Error loading chunks from md-bkp {entry.name}.```'
                )
            raise
        finally:
            self.load_confirmed = False
            self.loading_bkp = False
            self.process.start()

    async def _make_chunk_bkp(self, player: str, name: str) -> None:
        destination = self.chunk_bkps_dir / f'{name}.zip'
        destination.parent.mkdir(parents=True, exist_ok=True)

        self.waiting = True
        self.process.execute('save-off')
        self.process.execute('save-all')
        try:
            while self.waiting:
                await asyncio.sleep(1)

            self.server.send_response(player, f'Creando {name}.zip...')
            self._write_chunk_zip(destination, player)
            self.server.send_response(player, f'✔ chunk-bkp {name}.zip creado.')
            self.process.add_log(f'chunk-bkp {name}.zip created')
        finally:
            self.process.execute('save-on')
            self.creating_bkp = False
            self.waiting = False

    async def _update_chunk_bkp(self, player: str, name: str) -> None:
        zip_path = self.chunk_bkps_dir / f'{name}.zip'
        try:
            chunks_by_dim = self._read_zip_chunks_by_dim(zip_path)
            if not any(chunks_by_dim.values()):
                self.server.send_response(
                    player,
                    f'✖ El chunk-bkp {name}.zip no tiene registro de chunks.',
                )
                return

            self.files_to_zip[player] = chunks_by_dim

            self.waiting = True
            self.process.execute('save-off')
            self.process.execute('save-all')
            while self.waiting:
                await asyncio.sleep(1)

            self.server.send_response(player, f'Creando {name}.zip...')
            self._write_chunk_zip(zip_path, player)
            self.server.send_response(player, f'✔ chunk-bkp {name}.zip actualizado.')
            self.process.add_log(f'chunk-bkp {name}.zip updated')
        finally:
            self.process.execute('save-on')
            self.creating_bkp = False
            self.waiting = False

    def _write_chunk_zip(self, destination: Path, player: str) -> None:
        log_content: list[str] = []
        world_dir = self.process.path / 'server' / 'world'

        with zipfile.ZipFile(destination, 'w') as zipf:
            for dim in _DIMS:
                chunk_list = self.files_to_zip[player][dim]
                if not chunk_list:
                    continue

                for cx, cz in chunk_list:
                    log_content.append(f'{dim} : {cx},{cz}')

                region_groups = self._group_chunks_by_region(chunk_list)
                folders = _dim_folders(dim)
                for reg_name, index_map in region_groups.items():
                    target_indices = set(index_map.keys())
                    for folder in folders:
                        file_path = world_dir / folder / reg_name
                        if not file_path.is_file():
                            continue
                        extracted, ext_indices = _extract_chunks_from_mca(file_path.read_bytes(), target_indices)
                        if extracted is None:
                            continue
                        zipf.writestr(Path(folder, reg_name).as_posix(), extracted)
                        for idx in ext_indices:
                            cx, cz = index_map[idx]
                            mcc_name = f'c.{cx}.{cz}.mcc'
                            mcc_path = world_dir / folder / mcc_name
                            if mcc_path.is_file():
                                zipf.write(mcc_path, Path(folder, mcc_name).as_posix())

            now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_text = (
                f'Backup realizado por: {player}\n'
                f'Fecha: {now_str}\n'
                f'Chunks respaldados:\n' + '\n'.join(log_content)
            )
            zipf.writestr('bkp_log.txt', log_text)

    @staticmethod
    def _group_chunks_by_region(chunks: list[tuple[int, int]]) -> dict[str, dict[int, tuple[int, int]]]:
        grouped: dict[str, dict[int, tuple[int, int]]] = {}
        for cx, cz in chunks:
            reg_name, idx = _chunk_to_region(cx, cz)
            grouped.setdefault(reg_name, {})[idx] = (cx, cz)
        return grouped

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
    def _read_zip_chunks_by_dim(zip_path: Path) -> dict[str, list[tuple[int, int]]]:
        result: dict[str, list[tuple[int, int]]] = {dim: [] for dim in _DIMS}
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                if 'bkp_log.txt' not in zip_ref.namelist():
                    return result
                raw_lines = zip_ref.read('bkp_log.txt').decode('utf-8', errors='replace').splitlines()
        except (zipfile.BadZipFile, OSError):
            return result

        for line in raw_lines:
            if ' : ' not in line:
                continue
            dim_part, coords_part = (part.strip() for part in line.split(':', 1))
            if dim_part not in result or ',' not in coords_part:
                continue
            cx_str, cz_str = (p.strip() for p in coords_part.split(',', 1))
            try:
                chunk = (int(cx_str), int(cz_str))
            except ValueError:
                continue
            if chunk not in result[dim_part]:
                result[dim_part].append(chunk)
        return result

    @classmethod
    def _read_zip_chunks(cls, zip_path: Path) -> set[tuple[str, tuple[int, int]]]:
        by_dim = cls._read_zip_chunks_by_dim(zip_path)
        return {(dim, chunk) for dim, chunks in by_dim.items() for chunk in chunks}

    def _find_colliding_bkps(
        self,
        target_chunks: set[tuple[str, tuple[int, int]]],
        exclude_name: str | None = None,
    ) -> list[str]:
        if not target_chunks:
            return []
        collisions: list[str] = []
        for zip_path in sorted(self.chunk_bkps_dir.glob('*.zip'), key=lambda path: path.name):
            if zip_path.name == exclude_name:
                continue
            if target_chunks & self._read_zip_chunks(zip_path):
                collisions.append(zip_path.name)
        return collisions

    def _warn_collisions(
        self,
        player: str,
        target_chunks: set[tuple[str, tuple[int, int]]],
        exclude_name: str | None = None,
    ) -> None:
        collisions = self._find_colliding_bkps(target_chunks, exclude_name=exclude_name)
        if collisions:
            self.server.send_response(player, f'⚠ Comparte chunks con: {", ".join(collisions)}')

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
            if self._add_rect_chunks(player, dim):
                self._show_list(player)

    def _has_md_bkps(self) -> bool:
        return (self.process.plugins_dir / 'md-bkps.py').is_file() and self.process.backups_dir.is_dir()

    def _get_md_bkps(self) -> list[BackupEntry]:
        if not self._has_md_bkps():
            return []
        entries = list(self.process.list_backups())
        auto_idx = self.process.client.config.backups + 1
        auto_path = self.process.backups_dir / f'{self.process.name} {auto_idx}'
        auto_log = auto_path / 'backup_log.txt'
        if auto_path.is_dir() and auto_log.is_file():
            created_at = ''
            for line in auto_log.read_text(encoding='utf-8', errors='replace').splitlines():
                if line.startswith('Backup created on:'):
                    created_at = line.removeprefix('Backup created on:').strip()
                    break
            entries.append(BackupEntry(name=auto_path.name, path=auto_path, created_at=created_at, size_bytes=0))

        def _sort_key(e: BackupEntry) -> tuple[int, str]:
            suffix = e.name.removeprefix(f'{self.process.name} ')
            return (int(suffix), '') if suffix.isdigit() else (999999, e.name)

        return sorted(entries, key=_sort_key)

    def _has_chunks_selected(self, player: str) -> bool:
        return any(self.files_to_zip[player][dim] for dim in _DIMS)

    def _show_list(self, player: str) -> None:
        if player not in self.files_to_zip:
            self.server.send_response(player, 'Lista vacía.')
            return

        total = sum(len(self.files_to_zip[player][dim]) for dim in _DIMS)
        if total == 0:
            self.server.send_response(player, 'Lista vacía.')
            return

        lines: list[str] = [f'{player}, chunk list ({total}):']
        i = 0
        for dim in _DIMS:
            for cx, cz in self.files_to_zip[player][dim]:
                i += 1
                lines.append(f'{i} • {dim} : ({cx}, {cz})')
                if i >= 20 and total > 20:
                    lines.append(f'... y {total - 20} chunks más.')
                    self.server.send_response(player, lines)
                    return

        self.server.send_response(player, lines)

    def _show_bkps(self, player: str) -> None:
        zip_entries = sorted(
            ((path, self._read_zip_datetime(path)) for path in self.chunk_bkps_dir.glob('*.zip')),
            key=lambda item: (item[1], item[0].name),
        )
        if not zip_entries:
            self.server.send_response(player, 'No se han creado backups.')
            return

        self.server.send_response(player, 'Chunk-bkps disponibles:')
        now = datetime.now()

        for zip_path, creation_time in zip_entries:
            time_ago = self._format_time_ago(creation_time, now)
            log_info = self._format_zip_hover(zip_path)
            stem = zip_path.stem
            components = [
                hover_and_suggest(
                    '[>] ',
                    color='green',
                    suggest=f'{self.server.prefix}cb load-bkp {stem}',
                    hover='Load chunk-bkp',
                ),
                hover_and_suggest(
                    '[⥁] ',
                    color='aqua',
                    suggest=f'{self.server.prefix}cb update {stem}',
                    hover='Update chunk-bkp',
                ),
                hover_and_suggest(
                    '[x] ',
                    color='red',
                    suggest=f'{self.server.prefix}cb del-bkp {stem}',
                    hover='Del chunk-bkp',
                ),
                hover('[ℹ] ', color='yellow', hover=log_info),
                json.dumps({'text': f'{zip_path.name} [{creation_time.strftime("%Y-%m-%d %H:%M:%S")}] [{time_ago}]'}),
            ]
            self.server.execute(f'tellraw {player} {extras(components)}')

    @staticmethod
    def _read_zip_datetime(zip_path: Path) -> datetime:
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                if 'bkp_log.txt' in zip_ref.namelist():
                    lines = zip_ref.read('bkp_log.txt').decode('utf-8', errors='replace').splitlines()
                    for line in lines:
                        if line.startswith('Fecha:'):
                            raw = line.removeprefix('Fecha:').strip()
                            try:
                                return datetime.strptime(raw, '%Y-%m-%d %H:%M:%S')
                            except ValueError:
                                pass
        except Exception:
            pass
        return datetime.fromtimestamp(zip_path.stat().st_mtime)

    @staticmethod
    def _format_time_ago(dt: datetime, now: datetime) -> str:
        seconds = int((now - dt).total_seconds())
        if seconds < 60:
            return 'Hace unos segundos'
        days = seconds // 86400
        if days > 0:
            return f'Hace {days} día' if days == 1 else f'Hace {days} días'
        hours = seconds // 3600
        if hours > 0:
            return f'Hace {hours} hora' if hours == 1 else f'Hace {hours} horas'
        mins = seconds // 60
        return f'Hace {mins} minuto' if mins == 1 else f'Hace {mins} minutos'

    @staticmethod
    def _format_zip_hover(zip_path: Path) -> str:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            if 'bkp_log.txt' not in zip_ref.namelist():
                return 'Sin registro.'
            lines = zip_ref.read('bkp_log.txt').decode('utf-8', errors='replace').splitlines()

        author: str | None = None
        chunks: list[str] = []
        in_chunks = False
        for line in lines:
            if line.startswith('Backup realizado por:'):
                author = line.removeprefix('Backup realizado por:').strip()
            elif line.startswith('Chunks respaldados:'):
                in_chunks = True
            elif in_chunks and line.strip():
                chunks.append(line.strip())

        if author and chunks:
            preview = ' | '.join(chunks[:8])
            if len(chunks) > 8:
                preview += f' (+{len(chunks) - 8} más)'
            return f'Hecho por: {author} | {len(chunks)} chunks | {preview}'
        if author:
            return f'Hecho por: {author}'
        return 'Sin registro de autor.'

    @staticmethod
    def _pos_to_chunk(pos: tuple[float, float, float]) -> tuple[int, int]:
        return math.floor(pos[0] / 16), math.floor(pos[2] / 16)

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

    def _add_rect_chunks(self, player: str, dim: str) -> bool:
        pos1 = self.player_positions[player][dim]['pos1']
        pos2 = self.player_positions[player][dim]['pos2']
        if pos1 is None or pos2 is None:
            return False

        x_min, x_max = sorted([pos1[0], pos2[0]])
        z_min, z_max = sorted([pos1[2], pos2[2]])
        cx_min, cx_max = math.floor(x_min / 16), math.floor(x_max / 16)
        cz_min, cz_max = math.floor(z_min / 16), math.floor(z_max / 16)
        rect_count = (cx_max - cx_min + 1) * (cz_max - cz_min + 1)
        other_count = sum(len(chunks) for d, chunks in self.files_to_zip[player].items() if d != dim)
        if rect_count + other_count > _MAX_SELECTED_CHUNKS:
            self.server.send_response(
                player,
                f'✖ Selección demasiado grande ({rect_count:,} chunks; máximo {_MAX_SELECTED_CHUNKS:,}).',
            )
            return False

        self.files_to_zip[player][dim] = [
            (cx, cz)
            for cx in range(cx_min, cx_max + 1)
            for cz in range(cz_min, cz_max + 1)
        ]
        return True
