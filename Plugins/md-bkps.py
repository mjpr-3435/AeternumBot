from __future__ import annotations

import asyncio
import contextlib
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from Classes.AeServer import AeServer
from Classes.config import get_ae_servers
from dismanager.classes import BasePlugin, ManagedProcess
from dismanager.core.files import copy_tree_with_progress
from dismanager.core.managed_process import BackupEntry
from Utils.minecraft_text import extras, hover, hover_and_suggest


class plugin(BasePlugin):
    """Manual and daily automatic full-process backup manager."""

    process: ManagedProcess
    server: AeServer
    waiting: bool
    scheduled_load_backup: dict[str, BackupEntry]
    action_confirmed: bool
    creating_backup: bool
    last_auto_backup: datetime | None
    auto_task: asyncio.Task[None] | None

    def __init__(self, process: ManagedProcess) -> None:
        self.process = process
        self.server = get_ae_servers(process.client)[process.name.casefold()]
        self.waiting = False
        self.scheduled_load_backup = {}
        self.action_confirmed = False
        self.creating_backup = False
        self.last_auto_backup = self._read_backup_datetime(self._get_auto_backup_path())
        self.auto_task = None

    async def on_plugins_load(self) -> None:
        self.auto_task = asyncio.create_task(self._auto_backup_loop())

    def unload(self) -> None:
        if self.auto_task is not None and not self.auto_task.done():
            self.auto_task.cancel()

    async def on_process_log(self, log: str) -> None:
        if 'INFO]:' in log and log.rstrip().endswith('Saved the game') and self.waiting:
            self.waiting = False

    async def on_mc_player_command(self, player: str, message: str) -> None:
        if self.server.is_command(message, 'mdhelp'):
            self.server.show_command(player, 'bk help', 'Muestra los comandos del backup manager.')
            return

        if self.server.is_command(message, 'bk help'):
            self.server.show_command(player, 'bkps', 'Lista los backups del servidor.')
            self.server.show_command(player, 'mk-bkp <comment | default : None>', 'Crea un backup.')
            if player not in self.server.admins:
                return
            self.server.show_command(player, 'del-bkp <name>', 'Elimina el backup <name>.')
            self.server.show_command(player, 'load-bkp <name>', 'Carga el backup <name>.')
            self.server.show_command(player, 'bk confirm', 'Confirma la acción solicitada.')
            return

        if self.server.is_command(message, 'bkps'):
            self._show_bkps(player)
            return

        if self.server.is_command(message, 'mk-bkp'):
            comment = message.removeprefix(f'{self.server.prefix}mk-bkp').strip()
            if self.creating_backup:
                self.server.send_response(player, '✖ Alguien más está creando un backup ahorita.')
                return
            await self._make_bkp(player, comment or None)
            return

        if player not in self.server.admins:
            if (
                self.server.is_command(message, 'load-bkp')
                or self.server.is_command(message, 'bk confirm')
                or self.server.is_command(message, 'del-bkp')
            ):
                self.server.send_response(player, '✖ Comando reservado solo para administradores.')
            return

        backups_by_name = {entry.name: entry for entry in self._list_all_backups()}

        if self.server.is_command(message, 'load-bkp'):
            backup_name = message.removeprefix(f'{self.server.prefix}load-bkp').strip()
            entry = backups_by_name.get(backup_name)
            if entry is None:
                self.server.send_response(player, '✖ No hay un backup con ese nombre.')
                return

            self.scheduled_load_backup[player] = entry
            cmd = f'{self.server.prefix}bk confirm'
            tellraw_json = extras(
                [hover_and_suggest(cmd, color='gray', suggest=cmd, hover=cmd)],
                text=f'Para confirmar la carga de §d[{backup_name}]§7 utiliza ',
            )
            self.server.execute(f'tellraw {player} {tellraw_json}')
            return

        if self.server.is_command(message, 'bk confirm'):
            if player not in self.scheduled_load_backup:
                self.server.send_response(player, '✖ No has solicitado la carga o creación de ningún backup.')
                return
            if self.action_confirmed:
                self.server.send_response(player, '✖ Ya alguien más confirmó la carga o creación de un backup.')
                return

            self.action_confirmed = True
            for i in range(5):
                await asyncio.sleep(1)
                self.server.send_response('@a', f'El servidor se reiniciará en {5 - i} segundos.')

            if player in self.scheduled_load_backup:
                await self._load_bkp(player)
            return

        if self.server.is_command(message, 'del-bkp'):
            backup_name = message.removeprefix(f'{self.server.prefix}del-bkp').strip()
            entry = backups_by_name.get(backup_name)
            if entry is None:
                self.server.send_response(player, '✖ No hay un backup con ese nombre.')
                return

            shutil.rmtree(entry.path)
            self.server.send_response(player, f'✔ Backup {backup_name} eliminado.')
            self._show_bkps(player)

    async def _auto_backup_loop(self) -> None:
        try:
            while True:
                if self.last_auto_backup is not None:
                    elapsed = (datetime.now() - self.last_auto_backup).total_seconds()
                    wait_time = max(0.0, 24 * 3600 - elapsed)
                else:
                    wait_time = 0.0

                await asyncio.sleep(wait_time)

                if self.creating_backup:
                    await asyncio.sleep(60)
                    continue

                if await self._make_auto_bkp():
                    self.last_auto_backup = datetime.now()
        except asyncio.CancelledError:
            return

    async def _load_bkp(self, player: str) -> None:
        entry = self.scheduled_load_backup.pop(player)
        try:
            self.process.stop()
            while self.process.is_running():
                await asyncio.sleep(0.1)

            discord_message = await self.process.send_to_console(f'Unpacking the backup {entry.name}...')
            counter = [0, 0]

            def on_progress(copied: int, total: int) -> None:
                counter[0] = copied
                counter[1] = total

            task = asyncio.create_task(asyncio.to_thread(self.process.restore_backup, entry, on_progress))
            while not task.done():
                if counter[1] == 0:
                    await asyncio.sleep(0.1)
                else:
                    if discord_message is not None:
                        await discord_message.edit(
                            content=f'```md\n[md-bkps]: [{counter[0]}/{counter[1]}] files have been unpacked...\n```'
                        )
                    await asyncio.sleep(0.5)

            error: BaseException | None = None
            try:
                await task
            except BaseException as exc:
                error = exc
                await self.process.client.report_error(f'{self.process.name}: restore_backup()')

            if discord_message is not None:
                msg = (
                    '```md\n[md-bkps]: ✖ An error occurred while unpacking files.\n```'
                    if error is not None
                    else '```md\n[md-bkps]: ✔ The files have been successfully unpacked.\n```'
                )
                await discord_message.edit(content=msg)

            self.process.start()
        finally:
            self.action_confirmed = False

    async def _make_auto_bkp(self) -> bool:
        if self.creating_backup:
            return False

        self.creating_backup = True
        auto_path = self._get_auto_backup_path()
        discord_message = await self.process.send_to_console('[md-bkps]: Creating automatic backup...')
        counter = [0, 0]

        self.waiting = True
        self.process.execute('save-off')
        self.process.execute('save-all')

        try:
            while self.waiting:
                await asyncio.sleep(1)

            self.server.send_response('@a', '[md-bkps]: Creando backup automatico...')

            def on_progress(copied: int, total: int) -> None:
                counter[0] = copied
                counter[1] = total

            def _job() -> None:
                if auto_path.exists():
                    shutil.rmtree(auto_path)
                copy_tree_with_progress(self.process.path, auto_path, on_progress)
                auto_log = auto_path / 'backup_log.txt'
                auto_log.write_text(
                    f'Backup created on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n'
                    'Backup created by: auto\n'
                    'Comment: auto\n',
                    encoding='utf-8',
                )

            task = asyncio.create_task(asyncio.to_thread(_job))
            while not task.done():
                if counter[1] == 0:
                    await asyncio.sleep(0.1)
                else:
                    percent = counter[0] * 100 / counter[1]
                    self.server.send_response(
                        '@a',
                        f'[md-bkps]: §f{percent:6.2f}§6%§r '
                        'archivos copiados en backup automatico...',
                    )
                    if discord_message is not None:
                        await discord_message.edit(
                            content=(
                                f'```md\n[md-bkps]: [{counter[0]}/{counter[1]}] '
                                'files have been copying in auto backup...\n```'
                            )
                        )
                    await asyncio.sleep(1)

            try:
                await task
            except Exception:
                await self.process.client.report_error(f'{self.process.name}: make_auto_bkp()')
                self.server.send_response('@a', '[md-bkps]: Ocurrio un error mientras se creaba el backup automatico.')
                if discord_message is not None:
                    await discord_message.edit(
                        content='```md\n[md-bkps]: Error while creating automatic backup.\n```'
                    )
                return False

            self.server.send_response('@a', '[md-bkps]: El backup automatico se creo exitosamente.')
            if discord_message is not None:
                await discord_message.edit(
                    content='```md\n[md-bkps]: Automatic backup updated successfully.\n```'
                )
            return True
        finally:
            self.process.execute('save-on')
            self.creating_backup = False
            self.waiting = False

    async def _make_bkp(self, player: str, comment: str | None = None) -> None:
        self.creating_backup = True
        discord_message = await self.process.send_to_console('Creating backup...')
        self.waiting = True
        self.process.execute('save-off')
        self.process.execute('save-all')

        try:
            while self.waiting:
                await asyncio.sleep(1)

            self.server.send_response('@a', '[md-bkps]: Creando backup...')
            self._rotate_manual_backups_preserving_admin()

            counter = [0, 0]

            def on_progress(copied: int, total: int) -> None:
                counter[0] = copied
                counter[1] = total

            task = asyncio.create_task(
                asyncio.to_thread(self.process.make_backup, on_progress, force=True)
            )
            while not task.done():
                if counter[1] == 0:
                    await asyncio.sleep(0.1)
                else:
                    percent = counter[0] * 100 / counter[1]
                    self.server.send_response(
                        '@a',
                        f'[md-bkps]: §f{percent:6.2f}§6%§r '
                        'archivos copiados...',
                    )
                    if discord_message is not None:
                        await discord_message.edit(
                            content=f'```md\n[md-bkps]: [{counter[0]}/{counter[1]}] files have been copying...\n```'
                        )
                    await asyncio.sleep(1)

            try:
                backup_path = await task
            except Exception:
                await self.process.client.report_error(f'{self.process.name}: make_bkp()')
                self.server.send_response('@a', '[md-bkps]: Ocurrio un error mientras se copiaban los archivos.')
                if discord_message is not None:
                    await discord_message.edit(
                        content='```md\n[md-bkps]: ✖ An error occurred while copying files.\n```'
                    )
                return

            log_path = backup_path / 'backup_log.txt'
            with log_path.open('a', encoding='utf-8') as file:
                file.write(f'Backup created by: {player}\n')
                if comment:
                    file.write(f'Comment: {comment}\n')

            self.server.send_response('@a', '[md-bkps]: El backup se creo exitosamente.')
            if discord_message is not None:
                await discord_message.edit(
                    content='```md\n[md-bkps]: ✔ The backup have been successfully created.\n```'
                )
        finally:
            self.process.execute('save-on')
            self.creating_backup = False
            self.waiting = False

    def _rotate_manual_backups_preserving_admin(self) -> None:
        limit = self.process.client.config.backups
        manual = self._get_manual_backups()
        if len(manual) < limit:
            return

        metadata: list[dict[str, Any]] = []
        for entry in manual:
            date = self._read_backup_datetime(entry.path) or datetime.fromtimestamp(entry.path.stat().st_mtime)
            author = self._read_backup_author(entry.path)
            is_admin = author is None or author in self.server.admins
            metadata.append({'entry': entry, 'date': date, 'is_admin': is_admin})

        admin_backups = [m for m in metadata if m['is_admin']]
        ordered = sorted(metadata, key=lambda item: item['date'])
        if admin_backups:
            latest_admin = max(admin_backups, key=lambda item: item['date'])
            candidates = [m for m in ordered if m['entry'].name != latest_admin['entry'].name]
            victim = candidates[0] if candidates else ordered[0]
        else:
            victim = ordered[0]

        shutil.rmtree(victim['entry'].path)

        # Compact remaining manual backups to 1..(limit-1) so DisManager's make_backup()
        # shifts them cleanly to 2..limit without deleting the protected admin backup.
        survivors = [m for m in reversed(ordered) if m is not victim]
        temp_paths: list[Path] = []
        for idx, item in enumerate(survivors, start=1):
            src: Path = item['entry'].path
            tmp = self.process.backups_dir / f'.__tmp_rot_{self.process.name}_{idx}'
            if tmp.exists():
                shutil.rmtree(tmp)
            src.rename(tmp)
            temp_paths.append(tmp)
        for idx, tmp in enumerate(temp_paths, start=1):
            dest = self.process.backups_dir / f'{self.process.name} {idx}'
            if dest.exists():
                shutil.rmtree(dest)
            tmp.rename(dest)

    def _get_auto_backup_path(self) -> Path:
        auto_index = self.process.client.config.backups + 1
        return self.process.backups_dir / f'{self.process.name} {auto_index}'

    def _list_all_backups(self) -> list[BackupEntry]:
        entries = list(self.process.list_backups())
        auto_path = self._get_auto_backup_path()
        auto_log = auto_path / 'backup_log.txt'
        if auto_path.is_dir() and auto_log.is_file():
            dt = self._read_backup_datetime(auto_path)
            created_at = dt.strftime('%Y-%m-%d %H:%M:%S') if dt else ''
            entries.append(BackupEntry(name=auto_path.name, path=auto_path, created_at=created_at, size_bytes=0))

        def _sort_key(e: BackupEntry) -> tuple[int, str]:
            suffix = e.name.removeprefix(f'{self.process.name} ')
            return (int(suffix), '') if suffix.isdigit() else (999999, e.name)

        return sorted(entries, key=_sort_key)

    def _get_manual_backups(self) -> list[BackupEntry]:
        limit = self.process.client.config.backups
        prefix = f'{self.process.name} '
        result: list[BackupEntry] = []
        for entry in self.process.list_backups():
            if not entry.name.startswith(prefix):
                continue
            suffix = entry.name.removeprefix(prefix)
            if suffix.isdigit() and 1 <= int(suffix) <= limit:
                result.append(entry)
        return result

    @staticmethod
    def _read_backup_datetime(backup_path: Path) -> datetime | None:
        log_file = backup_path / 'backup_log.txt'
        if not log_file.is_file():
            return None

        for line in log_file.read_text(encoding='utf-8').splitlines():
            if not line.startswith('Backup created on:'):
                continue
            with contextlib.suppress(ValueError):
                return datetime.strptime(
                    line.removeprefix('Backup created on:').strip(),
                    '%Y-%m-%d %H:%M:%S',
                )
        return None

    @staticmethod
    def _read_backup_author(backup_path: Path) -> str | None:
        log_file = backup_path / 'backup_log.txt'
        if not log_file.is_file():
            return None

        for line in log_file.read_text(encoding='utf-8').splitlines():
            if line.startswith('Backup created by:'):
                return line.removeprefix('Backup created by:').strip()
        return None

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

    def _show_bkps(self, player: str) -> None:
        backups = self._list_all_backups()
        if not backups:
            self.server.send_response(player, 'No se han creado backups.')
            return

        self.server.send_response(player, 'Backups disponibles:')
        now = datetime.now()
        auto_name = self._get_auto_backup_path().name

        for entry in backups:
            dt = self._read_backup_datetime(entry.path) or datetime.fromtimestamp(entry.path.stat().st_mtime)
            date = dt.strftime('%Y-%m-%d %H:%M:%S')
            time_ago = self._format_time_ago(dt, now)
            comment: str | None = None
            author: str | None = None

            log_file = entry.path / 'backup_log.txt'
            if log_file.is_file():
                for line in log_file.read_text(encoding='utf-8').splitlines():
                    if line.startswith('Backup created by:'):
                        author = line.removeprefix('Backup created by:').strip()
                    elif line.startswith('Comment:'):
                        comment = line.removeprefix('Comment:').strip()

            components = [
                hover_and_suggest(
                    '[>] ',
                    color='green',
                    suggest=f'{self.server.prefix}load-bkp {entry.name}',
                    hover='Load backup',
                ),
                hover_and_suggest(
                    '[x] ',
                    color='red',
                    suggest=f'{self.server.prefix}del-bkp {entry.name}',
                    hover='Del backup',
                ),
                json.dumps({'text': f'{entry.name} ', 'color': 'aqua' if entry.name == auto_name else 'white'}),
                json.dumps({'text': f'[{date}] [{time_ago}] ', 'color': 'gray'}),
            ]
            if entry.name == auto_name:
                components.append(json.dumps({'text': '[AUTO] ', 'color': 'light_purple'}))
            if author:
                components.append(json.dumps({'text': f'by {author} ', 'color': 'dark_aqua'}))
            if comment:
                components.append(hover('[C]', color='gold', hover=comment))

            self.server.execute(f'tellraw {player} {extras(components)}')
