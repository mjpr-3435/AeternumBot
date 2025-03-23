import asyncio
import shutil
import os
import re

from Classes.AeServer import AeServer

class mdplugin():
    def __init__(self, server: AeServer):
        self.server                 = server
        self.files_to_copy          = {}
        self.action_confirmed       = False

    async def on_player_command(self, player: str, message: str):
        if not player in self.server.admins:
            return
        
        elif self.server.is_command(message, 'mdhelp'):
            self.server.show_command(player, 'ru help'           , 'Muestra los comandos del region updater.')

        elif self.server.is_command(message, 'ru help'):
            self.server.show_command(player, 'ru clear'          , 'Limpia tu lista.')
            self.server.show_command(player, 'ru list'           , 'Muestra tu lista de regiones.')
            self.server.show_command(player, 'ru add'            , 'Añade a tu lista una región.')
            self.server.show_command(player, 'ru update'         , 'Actualiza las regiones.')

        elif self.server.is_command(message, 'ru add'):
            raw_pos = await self.server.get_data(player, 'Pos')
            raw_pos = raw_pos[raw_pos.find('[') + 1 : raw_pos.find(']')].split(',')
            raw_dim = await self.server.get_data(player, 'Dimension')
            dim     = raw_dim.replace('"','').split(':')[1]
            pos     = tuple(float(x.strip()[:-1]) for x in raw_pos)
            reg     = self.pos_to_region(pos)

            if not player in self.files_to_copy.keys(): self.files_to_copy[player] = {'overworld':[],
                                                                        'the_nether':[],
                                                                        'the_end':[]}

            if not reg in self.files_to_copy[player][dim]: self.files_to_copy[player][dim].append(reg)

            self.show_list(player)
   
        elif self.server.is_command(message, 'ru list'):
            self.show_list(player)

        elif self.server.is_command(message, 'ru clear'):
            self.files_to_copy[player] = {'overworld':[],
                                    'the_nether':[],
                                    'the_end':[]}
            self.show_list(player)

        elif self.server.is_command(message, 'ru update'):

            if  not player in self.files_to_copy.keys() or \
                not self.files_to_copy[player]['overworld']  +\
                    self.files_to_copy[player]['the_nether'] +\
                    self.files_to_copy[player]['the_end']: 
                
                self.server.send_response(player, '✖ No has agregado ninguna región.')
                return
            
            elif self.action_confirmed:
                self.server.send_response(player, '✖ Alguien más ya solicitó la actualización de regiones.')
                return
            
            self.action_confirmed = True
            
            for i in range(5):
                await asyncio.sleep(1)
                self.server.send_response('@a', f'El servidor se reiniciará en {5-i} segundos.')
                
            smp_server = next(filter(lambda x: x.name == 'SMP', self.server.client.servers), None)
            
            if not smp_server:
                return
            
            elif smp_server.is_running():
                smp_server.execute('save-off')
                smp_server.execute('save-all')
                await asyncio.sleep(5)

            self.server.stop()

            while self.server.is_running():
                await asyncio.sleep(0.1)

            discord_message = await self.server.send_to_console(f'[reg-updater]: Copying files from SMP...')

            for dim in self.files_to_copy[player].keys():
                if dim == 'overworld':
                    entities, region, poi = 'entities', 'region', 'poi'
                elif dim == 'the_nether':
                    entities, region, poi = os.path.join('DIM-1','entities'), os.path.join('DIM-1','region'), os.path.join('DIM-1','poi')
                elif dim == 'the_end':
                    entities, region, poi = os.path.join('DIM1','entities'), os.path.join('DIM1','region'), os.path.join('DIM1','poi')
                
                for reg in self.files_to_copy[player][dim]:
                    for folder in [region, poi, entities]:
                        source = os.path.join(smp_server.path_files, 'server', 'world', folder, reg)
                        destination = os.path.join(self.server.path_files, 'server', 'world', folder, reg)
                        shutil.copy2(source, destination)

            await discord_message.edit(content = f'```md\n[reg-updater]: ✔ Files have been copied.\n```')

            if smp_server.is_running():
                smp_server.execute('save-on')
            
            self.server.start()

    def show_list(self, player : str):
        if not player in self.files_to_copy.keys():
            self.server.send_response(player, 'Lista vacía.')
            return
        
        msg = []
        i = 0
        for dim in self.files_to_copy[player].keys():
            for reg in self.files_to_copy[player][dim]:
                i += 1
                msg .append(f'{i} • {dim} : {reg}')
        
        if len(msg):
            msg.insert(0, f'{player}, region list:')
        else:
            msg = 'Lista vacía.'
        self.server.send_response(player, msg)

    def pos_to_region(self, pos : tuple):
        r_x = int(pos[0] // (32*16))
        r_z = int(pos[2] // (32*16))

        return f"r.{r_x}.{r_z}.mca"