from mcdis_rcon.utils import hover, extras
from Classes.AeServer import AeServer
import asyncio

class mdplugin():
    def __init__(self, server: AeServer):
        self.server = server

    async def on_player_command(self, player: str, message: str):
        if self.server.is_command(message, 'mdhelp'):
            self.server.show_command(player, f'ping <player | default : {player}>', 'Emite un sonido con origen en el jugador.')

        if self.server.is_command(message, 'ping'):
            target = message.removeprefix(f'{self.server.prefix}ping').strip()
            target = target if target else player
            
            if target not in self.server.online_players:
                self.server.send_response('El jugador no fue encontrado.')

            self.server.execute(f'execute at {target} run playsound minecraft:block.note_block.pling master @a ~ ~ ~ 1 1.6')
            await asyncio.sleep(0.15)
            self.server.execute(f'execute at {target} run playsound minecraft:block.note_block.pling master @a ~ ~ ~ 0.8 1.2')
