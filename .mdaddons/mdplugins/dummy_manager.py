from Classes.AeServer import AeServer
from mcdis_rcon.utils import hover_and_suggest, extras
import asyncio
import shutil
import os

class mdplugin():
    def __init__(self, server: AeServer):
        self.server = server

    async def on_player_command(self, player: str, message: str):
        presets_path = os.path.join(self.server.path_files, 'server', 'presets_mods')
        presets = [x for x in os.listdir(presets_path) if os.path.isdir(os.path.join(presets_path, x))]

        if self.server.is_command(message, 'mdhelp'):
            self.server.show_command(player, 'pd help', 'Muestra los comandos del presets manager.')

        elif self.server.is_command(message, 'pd help'):
            self.server.show_command(player, f"pd presets", "Muestra los presets disponibles.")
            self.server.show_command(player, f"pd load <preset>", "Carga el preset solicitado.")

        elif self.server.is_command(message, 'pd presets'):

            self.server.send_response(player, "Presets disponibles:")

            for preset in presets:
                dummy = [
                hover_and_suggest('[>] ' , color = 'green', suggest = f'!!pd load {preset}', hover = 'Load preset'),
                f'{{"text":"{preset}"}}'
                ]

                self.server.execute(f'tellraw {player} {extras(dummy)}')

        elif self.server.is_command(message, 'pd load'):
            preset = message.removeprefix(f'{self.server.prefix}pd load').strip()
            
            self.server.stop()

            while self.server.is_running():
                await asyncio.sleep(0.1)

            preset_prop_path = os.path.join(self.server.path_files, 'server', 'presets_properties', f'{preset}.properties')
            preset_mods_path = os.path.join(self.server.path_files, 'server', 'presets_mods', f'{preset}')

            prop_path = os.path.join(self.server.path_files, 'server', 'server.properties')
            mods_path = os.path.join(self.server.path_files, 'server', 'mods')
            
            if os.path.exists(mods_path):
                shutil.rmtree(mods_path)

            shutil.copytree(preset_mods_path, mods_path)
            shutil.copy2(preset_prop_path, prop_path)

            self.server.start()
        
        
