from __future__ import annotations

import asyncio
import hashlib
import os
import re
import shutil
import urllib.request
from pathlib import Path

import discord
from dismanager.classes import BasePlugin, ManagedProcess

from Classes import AeServer, get_ae_config, get_ae_servers

_MCA_VERSION = '2.7'
_MCA_URL = 'https://github.com/Querz/mcaselector/releases/download/2.7/mcaselector-2.7.jar'
_MCA_SHA256 = 'a5d248426a198487ef4001cc1b2d3e22342f88c8c53ab36c23af4f1cb43d5a91'
_REGION_NAME = re.compile(r'^r\.(-?\d+)\.(-?\d+)\.mca$')


class plugin(BasePlugin):
    """Offline world pruning driven by AeternumCarpet's exported MCA Selector CSV files."""

    process: ManagedProcess
    server: AeServer
    pending_player: str | None
    running: bool
    tool_directory: Path
    jar_path: Path
    work_directory: Path

    def __init__(self, process: ManagedProcess) -> None:
        self.process = process
        self.server = get_ae_servers(process.client)[process.name.casefold()]
        self.pending_player = None
        self.running = False
        self.tool_directory = Path(__file__).resolve().parent / 'world-trimmer'
        self.jar_path = self.tool_directory / f'mcaselector-{_MCA_VERSION}.jar'
        self.work_directory = self.tool_directory / 'work'

    def _operator(self) -> str:
        return get_ae_config(self.process.client).world_trimmer.operator

    async def on_mc_player_command(self, player: str, message: str) -> None:
        if self.server.is_command(message, 'mdhelp'):
            self.server.show_command(
                player,
                'trim help',
                'Poda el mundo fuera de las áreas exportadas por Carpet.',
            )
            return

        operator = self._operator()
        if self.server.is_command(message, 'trim help'):
            self.server.show_command(
                player,
                'trim',
                'Prepara una poda offline usando los CSV de AeternumCarpet.',
            )
            if player == operator:
                self.server.show_command(
                    player,
                    'trim confirm',
                    'Confirma la poda preparada. Detiene y reinicia el servidor.',
                )
            return

        if not self.server.is_command(message, 'trim'):
            return
        if player != operator:
            self.server.send_response(
                player,
                f'Solo {operator} puede preparar o confirmar la poda del mundo.',
            )
            return

        argument = message.removeprefix(f'{self.server.prefix}trim').strip().casefold()
        if argument == 'confirm':
            await self.confirm(player)
        elif not argument:
            await self.prepare(player)
        else:
            self.server.send_response(
                player,
                f'Usa {self.server.prefix}trim o {self.server.prefix}trim confirm.',
            )

    async def prepare(self, player: str) -> None:
        if self.running:
            self.server.send_response(player, 'Ya hay una poda en curso.')
            return
        try:
            await self._ensure_mca_selector()
            self._ensure_export_files_exist()
        except RuntimeError as error:
            self.server.send_response(player, f'No se puede preparar la poda: {error}')
            return

        self.pending_player = player
        counts = [
            f'{label}: {len(self._read_selection(csv_path))} chunks a preservar'
            for label, _, csv_path in self._dimensions()
        ]
        self.server.send_response(
            player,
            [
                'Poda preparada. Carpet es la fuente de verdad.',
                *counts,
                f'Usa {self.server.prefix}trim confirm para detener, podar y reiniciar.',
            ],
        )

    async def confirm(self, player: str) -> None:
        if self.running:
            self.server.send_response(player, 'Ya hay una poda en curso.')
            return
        if self.pending_player is None:
            self.server.send_response(player, f'Primero usa {self.server.prefix}trim para preparar la poda.')
            return
        if self.pending_player != player:
            self.server.send_response(player, 'La poda debe ser confirmada por quien la preparó.')
            return

        self.running = True
        stopped = False
        try:
            await self._log('[world-trimmer] Deteniendo servidor para poda offline...')
            self.process.stop()
            stopped = await self._wait_until_stopped()
            if not stopped:
                raise RuntimeError('el servidor no se detuvo dentro del tiempo esperado')

            for label, world_path, source_csv in self._dimensions():
                deletion_csv, preserved, existing = self._create_inverse_selection(
                    label, world_path, source_csv
                )
                if not existing:
                    await self._log(f'[world-trimmer] {label}: no hay chunks almacenados; se omite.')
                    continue
                if not preserved:
                    raise RuntimeError(
                        f'{label}: el CSV de preservación está vacío; se cancela por seguridad'
                    )
                deleting = existing - preserved
                if not deleting:
                    await self._log(f'[world-trimmer] {label}: {len(existing)} chunks, nada para borrar.')
                    continue
                await self._log(
                    f'[world-trimmer] {label}: preserva {len(existing & preserved)}, borra {len(deleting)} chunks.'
                )
                await self._run_mca_selector(label, world_path, deletion_csv)

            await self._log('[world-trimmer] Poda terminada correctamente.')
        except Exception as error:
            await self._log(f'[world-trimmer] ERROR: {error}')
            self.server.send_response(player, f'La poda falló: {error}')
        finally:
            self.pending_player = None
            self.running = False
            if stopped:
                await self._log('[world-trimmer] Iniciando servidor...')
                self.process.start()

    def _dimensions(self) -> tuple[tuple[str, Path, Path], ...]:
        server_root = self.process.path / 'server'
        config_dir = server_root / 'config'
        world = server_root / 'world'
        return (
            ('Overworld', world, config_dir / 'ExplorerManagerOverworldSelection.csv'),
            ('Nether', world / 'DIM-1', config_dir / 'ExplorerManagerNetherSelection.csv'),
            ('End', world / 'DIM1', config_dir / 'ExplorerManagerEndSelection.csv'),
        )

    async def _ensure_mca_selector(self) -> None:
        if shutil.which('java') is None:
            raise RuntimeError('no se encontró Java en PATH (MCA Selector requiere Java 21+)')
        self.tool_directory.mkdir(parents=True, exist_ok=True)
        if self.jar_path.exists() and self._sha256(self.jar_path) == _MCA_SHA256:
            return
        await self._log(f'[world-trimmer] Descargando MCA Selector {_MCA_VERSION}...')
        temporary = self.jar_path.with_suffix('.jar.part')
        await asyncio.to_thread(self._download, temporary)
        if self._sha256(temporary) != _MCA_SHA256:
            temporary.unlink(missing_ok=True)
            raise RuntimeError('falló la verificación SHA-256 de MCA Selector')
        os.replace(temporary, self.jar_path)

    def _ensure_export_files_exist(self) -> None:
        missing = [str(csv_path) for _, _, csv_path in self._dimensions() if not csv_path.is_file()]
        if missing:
            raise RuntimeError('faltan CSV de AeternumCarpet: ' + ', '.join(missing))

    def _create_inverse_selection(
        self, label: str, world_path: Path, source_csv: Path
    ) -> tuple[Path, set[tuple[int, int]], set[tuple[int, int]]]:
        preserved = self._read_selection(source_csv)
        existing = self._read_existing_chunks(world_path)
        deletion = existing - preserved
        self.work_directory.mkdir(parents=True, exist_ok=True)
        output = self.work_directory / f'{self.server.name.lower()}-{label.lower()}-delete.csv'
        with output.open('w', encoding='utf-8', newline='\n') as file:
            for chunk_x, chunk_z in sorted(
                deletion, key=lambda chunk: (chunk[0] // 32, chunk[1] // 32, chunk[0], chunk[1])
            ):
                file.write(f'{chunk_x // 32};{chunk_z // 32};{chunk_x};{chunk_z}\n')
        return output, preserved, existing

    @staticmethod
    def _read_selection(csv_path: Path) -> set[tuple[int, int]]:
        chunks: set[tuple[int, int]] = set()
        with csv_path.open(encoding='utf-8') as file:
            for line_number, line in enumerate(file, 1):
                if not line.strip():
                    continue
                fields = line.strip().split(';')
                if len(fields) != 4:
                    raise RuntimeError(f'CSV inválido en {csv_path}, línea {line_number}')
                chunks.add((int(fields[2]), int(fields[3])))
        return chunks

    @staticmethod
    def _read_existing_chunks(world_path: Path) -> set[tuple[int, int]]:
        chunks: set[tuple[int, int]] = set()
        for folder in ('region', 'poi', 'entities'):
            directory = world_path / folder
            if not directory.is_dir():
                continue
            for region_file in directory.glob('r.*.*.mca'):
                match = _REGION_NAME.match(region_file.name)
                if not match:
                    continue
                region_x, region_z = map(int, match.groups())
                with region_file.open('rb') as file:
                    locations = file.read(4096)
                if len(locations) != 4096:
                    continue
                for index in range(1024):
                    if locations[index * 4 : index * 4 + 3] != b'\0\0\0':
                        chunks.add((region_x * 32 + index % 32, region_z * 32 + index // 32))
        return chunks

    async def _run_mca_selector(self, label: str, world_path: Path, selection: Path) -> None:
        java = shutil.which('java')
        if java is None:
            raise RuntimeError('no se encontró Java en PATH')
        command = [
            java,
            '-jar',
            str(self.jar_path),
            '--mode',
            'delete',
            '--world',
            str(world_path),
            '--selection',
            str(selection),
        ]
        proc = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        progress = await self._log(f'[world-trimmer] {label}: iniciando MCA Selector...')

        lines: list[str] = []
        assert proc.stdout is not None
        while True:
            raw = await proc.stdout.readline()
            if not raw:
                break
            text = raw.decode('utf-8', errors='replace').rstrip()
            if not text.strip():
                continue
            lines.append(text)
            if len(lines) > 20:
                lines.pop(0)
            if progress is not None:
                await progress.edit(content=f'```md\n[world-trimmer] {label}: {text}\n```')

        await proc.wait()
        if proc.returncode != 0:
            raise RuntimeError(f'MCA Selector falló en {label} con código {proc.returncode}')

        for line in lines:
            await self._log(f'[world-trimmer] {label}: {line}')

    async def _wait_until_stopped(self) -> bool:
        for _ in range(720):
            if not self.process.is_running():
                return True
            await asyncio.sleep(0.25)
        return False

    async def _log(self, message: str) -> discord.Message | None:
        return await self.process.send_to_console(message)

    @staticmethod
    def _download(destination: Path) -> None:
        request = urllib.request.Request(_MCA_URL, headers={'User-Agent': 'AeternumBot-world-trimmer'})
        with urllib.request.urlopen(request, timeout=120) as response, destination.open('wb') as file:
            shutil.copyfileobj(response, file)

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open('rb') as file:
            for block in iter(lambda: file.read(1024 * 1024), b''):
                digest.update(block)
        return digest.hexdigest()
