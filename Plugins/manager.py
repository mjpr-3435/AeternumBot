from __future__ import annotations

import json

import psutil
from Classes.AeServer import AeServer
from Classes.config import get_ae_servers
from dismanager.classes import BasePlugin, ManagedProcess
from Utils.minecraft_text import extras, hover


class plugin(BasePlugin):
    """In-game process manager commands (``status``, ``start``, ``stop``, ``restart``, ``plreload``, ``adreload``)."""

    process: ManagedProcess
    server: AeServer

    def __init__(self, process: ManagedProcess) -> None:
        self.process = process
        self.server = get_ae_servers(process.client)[process.name.casefold()]

    async def on_mc_player_command(self, player: str, message: str) -> None:
        if self.server.is_command(message, 'mdhelp'):
            self.server.show_command(player, 'pm help', 'Muestra los comandos del processes manager.')
            return

        if self.server.is_command(message, 'pm help'):
            self.server.show_command(player, 'status', 'Muestra el estado de los procesos.')
            self.server.show_command(player, 'start <process>', 'Abrir el proceso.')
            if player not in self.server.admins:
                return
            self.server.show_command(player, f'stop <process | default : {self.server.name}>', 'Detener el proceso.')
            self.server.show_command(player, f'restart <process | default : {self.server.name}>', 'Reiniciar el proceso.')
            self.server.show_command(
                player,
                f'plreload <process | default : {self.server.name}>',
                'Recargar los plugins del proceso.',
            )
            self.server.show_command(player, 'adreload', 'Recargar los addons.')
            return

        if self.server.is_command(message, 'status'):
            self._send_status(player)
            return

        if self.server.is_command(message, 'start'):
            arg = message.removeprefix(f'{self.server.prefix}start').strip()
            if not arg:
                self.server.send_response(player, '✖ Debes proveer un argumento.')
                return
            target = self.process.client.find_process(arg)
            if target is None:
                self.server.send_response(player, '✖ No hay un proceso con ese nombre.')
                return
            if target.is_running():
                self.server.send_response(player, '✖ El proceso ya estaba abierto...')
                return
            self.server.send_response(player, f'[{target.name}] Abriendo proceso...')
            target.start()
            return

        if player not in self.server.admins:
            return

        if self.server.is_command(message, 'stop'):
            arg = message.removeprefix(f'{self.server.prefix}stop').strip()
            if not arg:
                self.server.send_response(player, '✔ Cerrando proceso...')
                self.process.stop()
                return
            target = self.process.client.find_process(arg)
            if target is None:
                self.server.send_response(player, '✖ No hay un proceso con ese nombre.')
                return
            if not target.is_running():
                self.server.send_response(player, '✖ El proceso no estaba abierto...')
                return
            self.server.send_response(player, f'[{target.name}] Cerrando proceso...')
            target.stop()
            return

        if self.server.is_command(message, 'plreload') or self.server.is_command(message, 'mdreload'):
            cmd_name = 'plreload' if self.server.is_command(message, 'plreload') else 'mdreload'
            arg = message.removeprefix(f'{self.server.prefix}{cmd_name}').strip()
            target = self.process if not arg else self.process.client.find_process(arg)
            if target is None:
                self.server.send_response(player, '✖ No hay un proceso con ese nombre.')
                return
            if arg and not target.is_running():
                self.server.send_response(player, '✖ El proceso no estaba abierto...')
                return
            count = await target.reload_plugins()
            self.server.send_response(player, f'✔ [{target.name}] {count} plugins recargados.')
            return

        if self.server.is_command(message, 'restart'):
            arg = message.removeprefix(f'{self.server.prefix}restart').strip()
            if not arg:
                self.server.send_response(player, '✔ Reiniciando proceso...')
                await self.process.restart()
                return
            target = self.process.client.find_process(arg)
            if target is None:
                self.server.send_response(player, '✖ No hay un proceso con ese nombre.')
                return
            if not target.is_running():
                self.server.send_response(player, '✖ El proceso no estaba abierto...')
                return
            self.server.send_response(player, f'[{target.name}] Reiniciando proceso...')
            await target.restart()
            return

        if self.server.is_command(message, 'adreload'):
            count = await self.process.client.reload_addons()
            self.server.send_response(player, f'✔ {count} addons recargados.')

    def _send_status(self, player: str) -> None:
        freq = psutil.cpu_freq()
        cpu_freq = f'{int(freq.current)} MHz' if freq is not None else 'N/A'
        cpu_load = f'{psutil.cpu_percent(interval=1)} %'

        ram = psutil.virtual_memory()
        ram_total = f'{ram.total / (1024 ** 3):.1f}'
        ram_used = f'{ram.used / (1024 ** 3):.1f}'
        ram_load = f'{ram.percent:.1f} %'

        disk = psutil.disk_usage('/')
        disk_total = f'{disk.total / (1024 ** 3):.1f}'
        disk_used = f'{disk.used / (1024 ** 3):.1f}'
        disk_load = f'{disk.percent:.1f} %'

        hover_hardware = [
            hover('§8[CPU] ', hover=f'Freq: {cpu_freq} | Load: {cpu_load}'),
            hover('§8[RAM] ', hover=f'Usage: {ram_used}/{ram_total} GB | Load: {ram_load}'),
            hover('§8[DISK] ', hover=f'Usage: {disk_used}/{disk_total} GB | Load: {disk_load}'),
        ]

        hover_servers = [
            hover(
                f'{"§f" if proc.is_running() else "§8"} [{proc.name}]',
                hover='Abierto' if proc.is_running() else 'Cerrado',
            )
            for proc in self.process.client.processes
        ]

        messages = [
            extras(hover_hardware, text='Recursos: ', color='gray'),
            json.dumps({'text': '--------------------------'}),
            extras(hover_servers, text='Servers: ', color='gray'),
        ]
        for line in messages:
            self.server.execute(f'tellraw {player} {line.replace(chr(10), "")}')
