from __future__ import annotations

import json

from Classes.AeServer import AeServer
from Classes.config import get_ae_servers
from dismanager.classes import BasePlugin, ManagedProcess
from Utils.minecraft_text import extras, hover


class plugin(BasePlugin):
    """Player location (``here``, ``where``) and permanent ``glow`` toggle."""

    process: ManagedProcess
    server: AeServer
    tour_glowing: set[str]

    def __init__(self, process: ManagedProcess) -> None:
        self.process = process
        self.server = get_ae_servers(process.client)[process.name.casefold()]
        self.tour_glowing = set()

    async def on_mc_player_command(self, player: str, message: str) -> None:
        args = message.split()

        if self.server.is_command(message, 'mdhelp'):
            self.server.show_command(player, 'loc help', 'Muestra los comandos de localización.')
            return

        if self.server.is_command(message, 'loc help'):
            self.server.show_command(player, 'here', 'Muestra la posición del jugador.')
            self.server.show_command(player, 'where <player>', 'Muestra la posición de otro jugador.')
            self.server.show_command(
                player,
                f'glow <player | default : {player}>',
                'Activa o desactiva glowing permanente (solo admins).',
            )
            return

        if self.server.is_command(message, 'here'):
            await self._show_position(player)
            return

        if self.server.is_command(message, 'where') and len(args) > 1:
            match = self._find_online_player(args[1])
            if match is None:
                self._send_error(player, 'Jugador no encontrado.')
                return
            await self._show_position(match)
            return

        if self.server.is_command(message, 'glow'):
            target_name = player
            if len(args) > 1:
                match = self._find_online_player(args[1])
                if match is None:
                    self._send_error(player, 'Jugador no encontrado.')
                    return
                target_name = match

            if player not in self.server.admins and target_name != player:
                self._send_error(player, 'No puedes aplicar esto a otro jugador.')
                return

            if target_name in self.tour_glowing:
                self.server.execute(f'effect clear {target_name} minecraft:glowing')
                self.tour_glowing.remove(target_name)
                msg = extras([
                    hover('§e[◯] ', hover='Glow desactivado'),
                    json.dumps({'text': 'Glowing permanente desactivado.', 'color': 'yellow'}),
                ])
            else:
                self.server.execute(f'effect give {target_name} minecraft:glowing 1000000 0 true')
                self.tour_glowing.add(target_name)
                msg = extras([
                    hover('§a[✔] ', hover='Glow activado'),
                    json.dumps({'text': 'Glowing permanente activado.', 'color': 'green'}),
                ])

            self.server.execute(f'tellraw {player} {msg}')

    def _find_online_player(self, name: str) -> str | None:
        target = name.casefold()
        all_players = self.server.online_players + self.server.bots
        return next((p for p in all_players if p.casefold() == target), None)

    def _send_error(self, player: str, text: str) -> None:
        msg = extras([
            hover('§c[✖] ', hover='Error'),
            json.dumps({'text': text, 'color': 'red'}),
        ])
        self.server.execute(f'tellraw {player} {msg}')

    async def _show_position(self, target: str) -> None:
        raw_pos = await self.server.get_data(target, 'Pos')
        raw_dim = await self.server.get_data(target, 'Dimension')
        if raw_pos is None or raw_dim is None:
            return

        coords_raw = raw_pos[raw_pos.find('[') + 1 : raw_pos.find(']')].split(',')
        dim1 = raw_dim.replace('"', '').split(':')[1]

        colors = {'overworld': 'green', 'the_nether': 'red', 'the_end': 'yellow'}
        labels = {'overworld': 'Overworld', 'the_nether': 'Nether', 'the_end': 'End'}
        pos1 = tuple(int(float(x.strip()[:-1])) for x in coords_raw)

        if dim1 in ('overworld', 'the_nether'):
            dim2 = 'the_nether' if dim1 == 'overworld' else 'overworld'
            scale = (1 / 8) if dim1 == 'overworld' else 8
            pos2 = tuple(int(float(x.strip()[:-1]) * scale) for x in coords_raw)
            message = extras(
                [
                    hover('[§k+X§r] ', color='dark_gray', hover='Qué miras?'),
                    hover(f'[{pos1[0]}, {pos1[1]}, {pos1[2]}]', color=colors[dim1], hover=labels[dim1]),
                    json.dumps({'text': ' -> ', 'color': 'gray'}),
                    hover(f'[{pos2[0]}, {pos1[1]}, {pos2[2]}]', color=colors[dim2], hover=labels[dim2]),
                ],
                text=f'@{target} ',
                color='gray',
            )
        elif dim1 == 'the_end':
            message = extras(
                [
                    hover('[§k+X§r] ', color='dark_gray', hover='Qué miras?'),
                    hover(f'[{pos1[0]}, {pos1[1]}, {pos1[2]}]', color=colors[dim1], hover=labels[dim1]),
                ],
                text=f'@{target} ',
                color='gray',
            )
        else:
            return

        self.server.execute(f'tellraw @a {message}')
        self.server.execute(f'effect give {target} minecraft:glowing 10 0 true')
