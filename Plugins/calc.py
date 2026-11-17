from __future__ import annotations

import math
from typing import Any

from dismanager.classes import BasePlugin, ManagedProcess

from Classes import AeServer, get_ae_servers
from Utils import hover_and_suggest

try:
    import numpy as np  # type: ignore[import-not-found]
except ImportError:
    np = None


class plugin(BasePlugin):
    """In-game math evaluator (``==<expr>`` and ``=?<expr>``)."""

    process: ManagedProcess
    server: AeServer
    restrictions: dict[str, Any]

    def __init__(self, process: ManagedProcess) -> None:
        self.process = process
        self.server = get_ae_servers(process.client)[process.name.casefold()]
        self.restrictions = {
            '__builtins__': None,
            'math': math,
            'abs': abs,
            'round': round,
            **({'np': np} if np is not None else {}),
        }

    async def on_mc_player_command(self, player: str, message: str) -> None:
        if self.server.is_command(message, 'mdhelp'):
            self.server.show_command(player, 'md calc', 'Muestra los comandos para usar la calculadora.')
        elif self.server.is_command(message, 'md calc'):
            self._show_calc_command(
                player,
                '==<expresión_matemática>',
                'Realiza el cálculo y devuelve el resultado.',
            )
            self._show_calc_command(
                player,
                '=?<expresión_matemática>',
                'Realiza el cálculo y devuelve el valor en SB, Stacks e Items.',
            )

    async def on_mc_player_message(self, player: str, message: str) -> None:
        if message.startswith('=='):
            expression = message.removeprefix('==')
            value = str(eval(expression, self.restrictions))
            self.server.send_response('@a', value, colour='gold')
            return

        if message.startswith('=?'):
            expression = message.removeprefix('=?')
            total = int(eval(expression, self.restrictions))
            if total <= 0:
                self.server.send_response(
                    '@a',
                    'El cálculo dió un valor igual o menor que cero.',
                    colour='gold',
                )
                return

            shulkers = total // (64 * 27)
            stacks = (total - shulkers * 64 * 27) // 64
            items = total % 64

            parts: list[str] = []
            if shulkers:
                parts.append(f'{shulkers} SB')
            if stacks:
                parts.append(f'64 x {stacks}')
            if items:
                parts.append(f'{items}')

            self.server.send_response('@a', ' + '.join(parts), colour='gold')

    def _show_calc_command(self, player: str, command: str, description: str) -> None:
        marked = command
        for sign in ('<', '>', ':', '|', '=', '?'):
            marked = marked.replace(sign, f'§6{sign}§f')

        tellraw_json = hover_and_suggest(marked, suggest=command, hover=marked)
        self.server.execute(f'tellraw {player} {tellraw_json}')
        self.server.send_response(player, f'  ↳ {description}')
