from __future__ import annotations

from Classes.AeServer import AeServer
from Classes.config import get_ae_servers
from dismanager.classes import BasePlugin, ManagedProcess


class plugin(BasePlugin):
    """Allow players on creative/testing servers to grant themselves OP."""

    process: ManagedProcess
    server: AeServer

    def __init__(self, process: ManagedProcess) -> None:
        self.process = process
        self.server = get_ae_servers(process.client)[process.name.casefold()]

    async def on_mc_player_command(self, player: str, message: str) -> None:
        if self.server.is_command(message, 'op'):
            self.server.execute(f'op {player}')
        elif self.server.is_command(message, 'mdhelp'):
            self.server.show_command(player, 'op', 'Otorga permisos de administrador al jugador.')
