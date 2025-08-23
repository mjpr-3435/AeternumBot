import asyncio
import zipfile
import os

from datetime import datetime
from mcdis_rcon.utils import hover_and_suggest, extras, hover, sct
from Classes.AeServer import AeServer

class mdplugin():
    def __init__(self, server: AeServer):
        self.server                 = server
        self.files_to_zip           = {}
        self.creating_bkp           = False
        self.waiting                = False
        self.scheduled_backup       = {}
        self.load_confirmed         = False

        self.reg_bkps_dir = os.path.join(self.server.path_plugins, 'reg-bkps')
        os.makedirs(self.reg_bkps_dir, exist_ok = True)

    async def   on_player_command(self, player: str, message: str):
        if not player in self.files_to_zip.keys():
            self.files_to_zip[player] = {'overworld':[],
                                    'the_nether':[],
                                    'the_end':[]}

        zips = [x for x in os.listdir(self.reg_bkps_dir) if x.endswith('.zip')]

        if self.server.is_command(message, 'mdhelp'):
            self.server.show_command(player, 'rb help'           , 'Muestra los comandos del regional backup.')

        elif self.server.is_command(message, 'rb help'):
            self.server.show_command(player, 'rb clear'          , 'Limpia tu lista.')
            self.server.show_command(player, 'rb list'           , 'Muestra tu lista de regiones.')
            self.server.show_command(player, 'rb add'            , 'Añade a tu lista una región.')
            self.server.show_command(player, 'rb del <index>'    , 'Elimina la región de índice <index> de tu lista.')
            self.server.show_command(player, 'rb mk-bkp <name>'  , 'Crea un reg-bkp <name>.zip con las regiones añadidas.')
            self.server.show_command(player, 'rb update <name>'  , 'Actualiza el reg-bkp <name>.zip reimportando regiones.')
            self.server.show_command(player, 'rb bkps'           , 'Lista los backups creados.')
            
            if not player in self.server.admins: return
            self.server.show_command(player, 'rb load-bkp <name>', 'Carga el reg-bkp <name>.zip.')
            self.server.show_command(player, 'rb del-bkp <name>' , 'Elimina el reg-bkp <name>.zip.')
            self.server.show_command(player, 'rb confirm'        , 'Confirma la carga del reg-bkp específicado.')


        elif self.server.is_command(message, 'rb add'):
            raw_pos = await self.server.get_data(player, 'Pos')
            raw_pos = raw_pos[raw_pos.find('[') + 1 : raw_pos.find(']')].split(',')
            raw_dim = await self.server.get_data(player, 'Dimension')
            dim     = raw_dim.replace('"','').split(':')[1]
            pos     = tuple(float(x.strip()[:-1]) for x in raw_pos)
            reg     = self.pos_to_region(pos)

            if not reg in self.files_to_zip[player][dim]: 
                self.files_to_zip[player][dim].append(reg)

            self.show_list(player)
        
        elif self.server.is_command(message, 'rb del'):
            index = int(message.removeprefix(f'{self.server.prefix}rb del'))
            
            if not any(len(self.files_to_zip[player][dim]) for dim in ['overworld', 'the_nether', 'the_end']): 
                self.server.send_response(player, 'Lista vacía.')
            else:
                i = 0
                for dim in self.files_to_zip[player].keys():
                    for reg in self.files_to_zip[player][dim]:
                        i += 1
                        if index == i:
                            self.files_to_zip[player][dim].remove(reg)
                self.show_list(player)
        
        elif self.server.is_command(message, 'rb list'):
            self.show_list(player)
        
        elif self.server.is_command(message, 'rb bkps'):
            self.show_bkps(player)

        elif self.server.is_command(message, 'rb clear'):
            self.files_to_zip[player] = {'overworld':[],
                                    'the_nether':[],
                                    'the_end':[]}
            self.show_list(player)

        elif self.server.is_command(message, 'rb mk-bkp'):
            name = message.removeprefix(f'{self.server.prefix}rb mk-bkp').strip()
            self.reg_bkps_dir = os.path.join(self.server.path_plugins, 'reg-bkps')

            if  not self.files_to_zip[player] or \
                not self.files_to_zip[player]['overworld']  +\
                    self.files_to_zip[player]['the_nether'] +\
                    self.files_to_zip[player]['the_end']: 
                self.server.send_response(player, '✖ No has agregado ninguna región.')
                return
            elif not name: 
                self.server.send_response(player, '✖ Debes proveer un nombre.')
                return
            elif self.creating_bkp: 
                self.server.send_response(player, '✖ Alguien más está creando un backup ahorita.')
                return
            
            self.creating_bkp = True
            
            await self.make_reg_bkp(player, name)

        elif self.server.is_command(message, 'rb update'):
            name = message.removeprefix(f'{self.server.prefix}rb update').strip()

            if not name or not name + '.zip' in zips: 
                self.server.send_response(player, '✖ Debes proveer un nombre en la lista.')
                return
            elif self.creating_bkp: 
                self.server.send_response(player, '✖ Alguien más está creando un backup ahorita.')
                return

            self.creating_bkp = True
            
            await self.update_reg_bkp(player, name)

        elif not player in self.server.admins and self.server.name == 'SMP': return

        elif self.server.is_command(message, 'rb load-bkp'):
            zip = message.removeprefix(f'{self.server.prefix}rb load-bkp').strip() + '.zip'

            if zip in zips:
                self.scheduled_backup[player] = zip

                dummy = extras(
                [hover_and_suggest('!!rb confirm' , color= 'dark_gray', suggest = '!!rb confirm', hover = '!!rb confirm')],
                text = f"Para confirmar la carga de §d[{zip}]§7 utiliza "
                )

                self.server.execute(f'tellraw {player} {dummy}')
            else:
                self.server.send_response(player, '✖ No hay un reg-bkp con ese nombre.')
                
        elif self.server.is_command(message, 'rb confirm'):
            if not player in self.scheduled_backup.keys(): 
                self.server.send_response(player, '✖ No has solicitado la carga de ningún backup.')
                return
            
            elif self.load_confirmed: 
                self.server.send_response(player, '✖ Ya alguien más confirmo la carga de un backup.')
                return
            
            self.load_confirmed = True

            for i in range(5):
                await asyncio.sleep(1)
                self.server.send_response('@a', f'El servidor se reiniciará en {5-i} segundos.')

            await self.load_reg_bkp(player)

        elif self.server.is_command(message, 'rb del-bkp'):
            zip = message.removeprefix(f'{self.server.prefix}rb del-bkp').strip() + '.zip'

            if zip in zips:
                os.remove(os.path.join(self.reg_bkps_dir, zip))
                self.show_bkps(player)
                self.server.send_response(player, f'✔ reg-bkp {zip} eliminado.')
            else:
                self.server.send_response(player, '✖ No hay un reg-bkp con ese nombre.')


    async def   listener_events(self, log : str):
        if not 'INFO]:' in log: 
            pass
            
        elif log.endswith('Saved the game') and self.waiting:
                self.waiting = False

    async def   load_reg_bkp(self, player: str):
        zip = self.scheduled_backup[player]

        self.server.stop()

        while self.server.is_running():
            await asyncio.sleep(0.1)

        discord_message = await self.server.send_to_console(f'[reg-bkps]: Unpacking reg-bkp {zip}...')

        source = os.path.join(self.server.path_plugins, 'reg-bkps', zip)
        destination = os.path.join(self.server.path_files, 'server', 'world')

        with zipfile.ZipFile(source, 'r') as zip_ref:
            for file in zip_ref.namelist():
                zip_ref.extract(file, destination)
        
        log_path = os.path.join(destination, 'bkp_log.txt')
        if os.path.exists(log_path): os.remove(log_path)

        await discord_message.edit(content = f'```md\n[reg-bkps]: ✔ Reg-bkp {zip} unpacked.```')

        self.server.start()

    async def   make_reg_bkp(self, player:str, name:str):
        destination = os.path.join(self.reg_bkps_dir, f'{name}.zip')
        os.makedirs(os.path.dirname(destination), exist_ok = True)

        self.waiting = True

        self.server.execute('save-off')
        self.server.execute('save-all')

        while self.waiting:
            await asyncio.sleep(1)

        self.server.send_response(player, f'Creando {name}.zip...')
        log_content = []
        
        with zipfile.ZipFile(destination, 'w') as zipf:
            for dim in self.files_to_zip[player].keys():
                if dim == 'overworld':
                    entities, region, poi = 'entities', 'region', 'poi'
                elif dim == 'the_nether':
                    entities, region, poi = os.path.join('DIM-1','entities'), os.path.join('DIM-1','region'), os.path.join('DIM-1','poi')
                elif dim == 'the_end':
                    entities, region, poi = os.path.join('DIM1','entities'), os.path.join('DIM1','region'), os.path.join('DIM1','poi')

                for reg in self.files_to_zip[player][dim]:
                    for folder in [region, poi, entities]:
                        file_path = os.path.join(self.server.path_files, 'server', 'world', folder, reg)
                        zipf.write(file_path, os.path.join(folder, reg))
                        
                    log_content.append(f'{dim} : {reg}')

            log_text = f"Archivos respaldados:\n" + "\n".join(log_content)
            zipf.writestr("bkp_log.txt", log_text)

        self.server.execute('save-on')
        self.server.send_response(player, f'✔ reg-bkp {name}.zip creado.')
        self.server.add_log(f'reg-bkp {name}.zip created')
        self.creating_bkp = False

    async def   update_reg_bkp(self, player:str, name:str):
        zip_path = os.path.join(self.reg_bkps_dir, f'{name}.zip')
        os.makedirs(os.path.dirname(zip_path), exist_ok = True)
        log_info = ''

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            if 'bkp_log.txt' in zip_ref.namelist():
                log_info = zip_ref.read('bkp_log.txt').decode().split('\n')[1:]
            else:
                self.server.send_response(player, f'✖ El reg-bkp {name}.zip no tiene registro de regiones.')
                return

        self.files_to_zip[player] = {'overworld':[],
                                     'the_nether':[],
                                     'the_end':[]}
        
        for log in log_info:
            dim = log.split(':')[0].strip()
            region = log.split(':')[1].strip()

            self.files_to_zip[player][dim].append(region)

        self.waiting = True

        self.server.execute('save-off')
        self.server.execute('save-all')

        while self.waiting:
            await asyncio.sleep(1)

        self.server.send_response(player, f'Creando {name}.zip...')
        log_content = []
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for dim in self.files_to_zip[player].keys():
                if dim == 'overworld':
                    entities, region, poi = 'entities', 'region', 'poi'
                elif dim == 'the_nether':
                    entities, region, poi = os.path.join('DIM-1','entities'), os.path.join('DIM-1','region'), os.path.join('DIM-1','poi')
                elif dim == 'the_end':
                    entities, region, poi = os.path.join('DIM1','entities'), os.path.join('DIM1','region'), os.path.join('DIM1','poi')

                for reg in self.files_to_zip[player][dim]:
                    for folder in [region, poi, entities]:
                        file_path = os.path.join(self.server.path_files, 'server', 'world', folder, reg)
                        zipf.write(file_path, os.path.join(folder, reg))
                        
                    log_content.append(f'{dim} : {reg}')

            log_text = f"Archivos respaldados:\n" + "\n".join(log_content)
            zipf.writestr("bkp_log.txt", log_text)

        self.server.execute('save-on')
        self.server.send_response(player, f'✔ reg-bkp {name}.zip actualizado.')
        self.server.add_log(f'reg-bkp {name}.zip updated')
        self.creating_bkp = False

    def         show_list(self, player : str):
        if not player in self.files_to_zip.keys():
            self.server.send_response(player, 'Lista vacía.')
            return
        
        msg = []
        i = 0
        for dim in self.files_to_zip[player].keys():
            for reg in self.files_to_zip[player][dim]:
                i += 1
                msg .append(f'{i} • {dim} : {reg}')
        
        if len(msg):
            msg.insert(0, f'{player}, region list:')
        else:
            msg = 'Lista vacía.'
        self.server.send_response(player, msg)

    def         show_bkps(self, player : str):
        self.reg_bkps_dir = os.path.join(self.server.path_plugins, 'reg-bkps')
        zips = [x for x in os.listdir(self.reg_bkps_dir) if x.endswith('.zip')]
        zips.sort()
        
        if not zips:
            self.server.send_response(player, 'No se han creado backups.')
            return
        
        self.server.send_response(player, 'Reg-bkps disponibles:')

        now = datetime.now()

        for zip in zips:
            zip_path = os.path.join(self.reg_bkps_dir, zip)
            creation_time = datetime.fromtimestamp(os.path.getctime(zip_path))
            time_diff = now - creation_time

            if time_diff.days > 0:
                time_ago = f"Hace {time_diff.days} días"
            elif time_diff.seconds >= 3600:
                time_ago = f"Hace {time_diff.seconds // 3600} horas"
            elif time_diff.seconds >= 60:
                time_ago = f"Hace {time_diff.seconds // 60} minutos"
            else:
                time_ago = "Hace unos segundos"

            log_info = ''

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                if 'bkp_log.txt' in zip_ref.namelist():
                    log_info = zip_ref.read('bkp_log.txt').decode().split('\n')
                    log_info = ' | '.join(log_info[1:])
                else:
                    log_info = 'Sin registro.'

            dummy = [
            hover_and_suggest('[>] ' , color = 'green', suggest = f'!!rb load-bkp {zip.removesuffix(".zip")}', hover = 'Load reg-bkp'),
            hover_and_suggest('[⥁] ', color = 'aqua', suggest = f'!!rb update {zip.removesuffix(".zip")}', hover = 'Update reg-bkp'),
            hover_and_suggest('[x] ' , color = 'red', suggest = f'!!rb del-bkp {zip.removesuffix(".zip")}', hover = 'Del reg-bkp'),
            hover('[ℹ] ', color='yellow', hover = log_info),
            f'{{"text":"{zip} [{creation_time.strftime("%Y-%m-%d %H:%M:%S")}] [{time_ago}]"}}'
            ]

            self.server.execute(f'tellraw {player} {extras(dummy)}')

    def         pos_to_region(self, pos : tuple):
        r_x = int(pos[0] // (32*16))
        r_z = int(pos[2] // (32*16))

        return f"r.{r_x}.{r_z}.mca"