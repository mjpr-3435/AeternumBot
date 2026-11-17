from __future__ import annotations

import asyncio
import shutil
from pathlib import Path

from Classes.AeServer import AeServer
from Classes.config import get_ae_servers
from dismanager.classes import BasePlugin, ManagedProcess
from Utils.rcon import rcon_execute

_DIMS = ('overworld', 'the_nether', 'the_end')
_PAPER_WORLDS = {
    'overworld': 'world',
    'the_nether': 'world_nether',
    'the_end': 'world_the_end',
}


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
    """Sync or delete selected SMP world regions on MMP/PMP."""

    process: ManagedProcess
    server: AeServer
    files_to_copy: dict[str, dict[str, list[str]]]
    files_to_remove: dict[str, dict[str, list[str]]]
    copy_positions: dict[str, dict[str, dict[str, tuple[float, float, float] | None]]]
    remove_positions: dict[str, dict[str, dict[str, tuple[float, float, float] | None]]]
    action_confirmed: bool

    def __init__(self, process: ManagedProcess) -> None:
        self.process = process
        self.server = get_ae_servers(process.client)[process.name.casefold()]
        self.files_to_copy = {}
        self.files_to_remove = {}
        self.copy_positions = {}
        self.remove_positions = {}
        self.action_confirmed = False

    async def on_mc_player_command(self, player: str, message: str) -> None:
        if self.server.is_command(message, 'mdhelp'):
            self.server.show_command(player, 'ru help', 'Muestra los comandos del region updater.')
            return

        if self.server.is_command(message, 'ru help'):
            self.server.show_command(player, 'ru clear', 'Limpia tu lista.')
            self.server.show_command(player, 'ru list', 'Muestra tu lista de regiones.')
            self.server.show_command(player, 'ru add', 'Añade a tu lista una región para actualizar.')
            self.server.show_command(player, 'ru pos1', 'Primera esquina del rectángulo de actualización.')
            self.server.show_command(player, 'ru pos2', 'Segunda esquina del rectángulo de actualización.')
            self.server.show_command(player, 'rm add', 'Añade a tu lista una región para remover.')
            self.server.show_command(player, 'rm pos1', 'Primera esquina del rectángulo de borrado.')
            self.server.show_command(player, 'rm pos2', 'Segunda esquina del rectángulo de borrado.')
            self.server.show_command(player, 'ru update', 'Actualiza las regiones.')
            return

        if self.server.is_command(message, 'ru add'):
            await self._add_current_region(player, self.files_to_copy)
            return

        if self.server.is_command(message, 'rm add'):
            await self._add_current_region(player, self.files_to_remove)
            return

        if self.server.is_command(message, 'ru pos1'):
            await self._set_corner(player, self.files_to_copy, self.copy_positions, 'pos1', 'pos2', for_removal=False)
            return

        if self.server.is_command(message, 'ru pos2'):
            await self._set_corner(player, self.files_to_copy, self.copy_positions, 'pos2', 'pos1', for_removal=False)
            return

        if self.server.is_command(message, 'rm pos1'):
            await self._set_corner(player, self.files_to_remove, self.remove_positions, 'pos1', 'pos2', for_removal=True)
            return

        if self.server.is_command(message, 'rm pos2'):
            await self._set_corner(player, self.files_to_remove, self.remove_positions, 'pos2', 'pos1', for_removal=True)
            return

        if self.server.is_command(message, 'ru list'):
            self._show_list(player)
            return

        if self.server.is_command(message, 'ru clear'):
            self.files_to_copy[player] = {dim: [] for dim in _DIMS}
            self.files_to_remove[player] = {dim: [] for dim in _DIMS}
            self.copy_positions[player] = {dim: {'pos1': None, 'pos2': None} for dim in _DIMS}
            self.remove_positions[player] = {dim: {'pos1': None, 'pos2': None} for dim in _DIMS}
            self._show_list(player)
            return

        if self.server.is_command(message, 'ru update'):
            await self._update_regions(player)

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

    async def _add_current_region(
        self,
        player: str,
        target_map: dict[str, dict[str, list[str]]],
    ) -> None:
        pos_dim = await self._get_player_position(player)
        if pos_dim is None:
            return
        pos, dim = pos_dim
        reg = self._pos_to_region(pos)

        player_map = target_map.setdefault(player, {d: [] for d in _DIMS})
        if reg not in player_map[dim]:
            player_map[dim].append(reg)

        self._show_list(player)

    async def _set_corner(
        self,
        player: str,
        target_map: dict[str, dict[str, list[str]]],
        pos_map: dict[str, dict[str, dict[str, tuple[float, float, float] | None]]],
        corner: str,
        other: str,
        *,
        for_removal: bool,
    ) -> None:
        pos_dim = await self._get_player_position(player)
        if pos_dim is None:
            return
        pos, dim = pos_dim
        player_pos = pos_map.setdefault(player, {d: {'pos1': None, 'pos2': None} for d in _DIMS})
        player_pos[dim][corner] = pos
        self.server.send_response(player, f'✔ {corner.capitalize()} establecida')

        pos1 = player_pos[dim]['pos1']
        pos2 = player_pos[dim]['pos2']
        if pos1 is None or pos2 is None:
            return

        region_folder = self._source_region_folder(dim, for_removal=for_removal)
        if region_folder is None or not region_folder.is_dir():
            return

        x_min, x_max = sorted([pos1[0], pos2[0]])
        z_min, z_max = sorted([pos1[2], pos2[2]])
        player_regions = target_map.setdefault(player, {d: [] for d in _DIMS})
        for reg_path in region_folder.glob('*.mca'):
            r_x, r_z = map(int, reg_path.stem[2:].split('.'))
            reg_x_min = r_x * 512
            reg_x_max = reg_x_min + 511
            reg_z_min = r_z * 512
            reg_z_max = reg_z_min + 511
            if (
                not (reg_x_max < x_min or reg_x_min > x_max or reg_z_max < z_min or reg_z_min > z_max)
                and reg_path.name not in player_regions[dim]
            ):
                player_regions[dim].append(reg_path.name)
        self._show_list(player)

    def _source_region_folder(self, dim: str, *, for_removal: bool) -> Path | None:
        if for_removal:
            if self.server.name == 'PMP':
                return self.process.path / 'server' / _PAPER_WORLDS.get(dim, 'world') / 'region'
            base = self.process.path / 'server' / 'world'
        else:
            smp_process = self.process.client.find_process('SMP')
            if smp_process is None:
                return None
            base = smp_process.path / 'server' / 'world'

        if dim == 'overworld':
            return base / 'region'
        if dim == 'the_nether':
            return base / 'DIM-1' / 'region'
        if dim == 'the_end':
            return base / 'DIM1' / 'region'
        raise ValueError(f'Dimensión desconocida: {dim}')

    async def _update_regions(self, player: str) -> None:
        copy_d = self.files_to_copy.get(player, {})
        rem_d = self.files_to_remove.get(player, {})
        combined = [reg for d in _DIMS for reg in copy_d.get(d, [])] + [
            reg for d in _DIMS for reg in rem_d.get(d, [])
        ]

        if not combined:
            self.server.send_response(player, '✖ No has agregado ninguna región.')
            return
        if self.action_confirmed:
            self.server.send_response(player, '✖ Alguien más ya solicitó la actualización de regiones.')
            return

        smp_server = get_ae_servers(self.process.client).get('smp')
        if smp_server is None:
            return

        self.action_confirmed = True
        smp_saved_off = False
        try:
            for i in range(5):
                await asyncio.sleep(1)
                self.server.send_response('@a', f'El servidor se reiniciará en {5 - i} segundos.')

            if smp_server.is_running() and smp_server.rcon_port is not None:
                smp_saved_off = True
                await rcon_execute('127.0.0.1', smp_server.rcon_port, smp_server.rcon_password, 'save-off')
                await rcon_execute('127.0.0.1', smp_server.rcon_port, smp_server.rcon_password, 'save-all flush')

            self.process.stop()
            while self.process.is_running():
                await asyncio.sleep(0.1)

            discord_message = await self.process.send_to_console('[reg-updater]: Copying files from SMP...')

            for dim, regions in copy_d.items():
                for folder in _dim_folders(dim):
                    for reg in regions:
                        source = smp_server.path / 'server' / 'world' / folder / reg
                        if not source.is_file():
                            continue
                        destination = self._destination_path(dim, folder, reg)
                        destination.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(source, destination)

            for dim, regions in rem_d.items():
                for folder in _dim_folders(dim):
                    for reg in regions:
                        target = self._destination_path(dim, folder, reg)
                        target.unlink(missing_ok=True)

            if discord_message is not None:
                await discord_message.edit(content='```md\n[reg-updater]: ✔ Files have been copied.\n```')

            self.process.start()
        finally:
            if smp_saved_off and smp_server.is_running() and smp_server.rcon_port is not None:
                await rcon_execute('127.0.0.1', smp_server.rcon_port, smp_server.rcon_password, 'save-on')
            self.action_confirmed = False

    def _destination_path(self, dim: str, folder: str, reg: str) -> Path:
        if self.server.name == 'PMP':
            world = _PAPER_WORLDS.get(dim, 'world')
            return self.process.path / 'server' / world / Path(folder).name / reg
        return self.process.path / 'server' / 'world' / folder / reg

    def _show_list(self, player: str) -> None:
        if player not in self.files_to_copy and player not in self.files_to_remove:
            self.server.send_response(player, 'Lista vacía.')
            return

        lines: list[str] = []
        i = 0
        for dim in _DIMS:
            for reg in self.files_to_copy.get(player, {}).get(dim, []):
                i += 1
                lines.append(f'{i} • ru -> {dim} : {reg}')
        for dim in _DIMS:
            for reg in self.files_to_remove.get(player, {}).get(dim, []):
                i += 1
                lines.append(f'{i} • rm -> {dim} : {reg}')

        if lines:
            lines.insert(0, f'{player}, region list:')
            self.server.send_response(player, lines)
        else:
            self.server.send_response(player, 'Lista vacía.')

    @staticmethod
    def _pos_to_region(pos: tuple[float, float, float]) -> str:
        r_x = int(pos[0] // (32 * 16))
        r_z = int(pos[2] // (32 * 16))
        return f'r.{r_x}.{r_z}.mca'
