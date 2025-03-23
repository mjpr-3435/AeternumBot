import math
import numpy as np
from Classes.AeServer import AeServer
from mcdis_rcon.utils import hover_and_suggest

class mdplugin():
    def __init__(self, server: AeServer):
        self.server = server
        self.restrictions = {
            "__builtins__": None,
            "math": math,
            "abs": abs,
            "round": round,
            "np": np
        }

    async def   on_player_command     (self, player: str, message: str):
        if self.server.is_command(message, 'mdhelp'):
            self.server.show_command(player, "md calc", "Muestra los comandos para usar la calculadora.")
        
        elif self.server.is_command(message, 'md calc'):
            self.show_calc_command(player, "==<expresion_matemática>", "Realiza el cálculo y devuelve el resultado.")
            self.show_calc_command(player, "=?<expresion_matemática>", "Realiza el cálculo y devuelve el valor en SB, Stacks e Items.")
            
    async def   on_player_message(self, player: str, message: str):
        if message.startswith('=='):
            expresion = message.removeprefix('==')
            value = str(eval(expresion, self.restrictions))
            self.server.send_response('@a', value, colour = 'gold')

        if message.startswith('=?'):
            expresion = message.removeprefix('=?')
            total = eval(expresion, self.restrictions)
            total = int(total)

            if not total > 0:
                self.server.send_response('@a', 'El cálculo dió un valor igual o menor que cero.', colour = 'gold')
                return

            shulkers = total//(64*27)
            stacks = (total - shulkers*64*27)//64
            items = total%64

            values = [] 

            if shulkers: values.append(f'{shulkers} SB')
            if stacks: values.append(f'64 x {stacks}')
            if items: values.append(f'{items}')

            value = ' + '.join(values)

            self.server.send_response('@a', value, colour = 'gold')

    def         show_calc_command(self, player: str, command: str, description: str):
            signs = ['<', '>', ':', '|', '=', '?']
            mrkd_command = f'{command}'
            
            for sign in signs: 
                mrkd_command = mrkd_command.replace(sign, f'§6{sign}§f')
            
            description = '  ↳ ' + description

            self.server.execute(f'tellraw {player} {hover_and_suggest(mrkd_command, suggest = f"{command}", hover = mrkd_command)}')
            self.server.send_response(player, description)