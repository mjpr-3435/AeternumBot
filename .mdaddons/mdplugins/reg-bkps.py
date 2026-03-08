import asyncio
import zipfile
import os

from datetime import datetime
from mcdis_rcon.utils import hover_and_suggest, extras, hover, write_in_file, read_file
from Classes.AeServer import AeServer

class mdplugin():
    def __init__(self, server: AeServer):
        self.server                 = server
        self.files_to_zip           = {}
        self.creating_bkp           = False
        self.waiting                = False
        self.scheduled_backup       = {}
        self.player_positions       = {}
        self.load_confirmed         = False
        self.whitelisted_players    = set()

        self.reg_bkps_dir = os.path.join(self.server.path_plugins, 'reg-bkps')
        os.makedirs(self.reg_bkps_dir, exist_ok = True)
        self.whitelist_text_path = os.path.join(self.reg_bkps_dir, 'whitelist.txt')

        if not os.path.exists(self.whitelist_text_path):
            write_in_file(self.whitelist_text_path, '')

        self.whitelisted_players = self.load_whitelist()

    async def   on_player_command(self, player: str, message: str):
        if player not in self.files_to_zip:
            self.files_to_zip[player] = {'overworld': [], 'the_nether': [], 'the_end': []}

        if player not in self.player_positions:
            self.player_positions[player] = {
                'overworld':  {'pos1': None, 'pos2': None},
                'the_nether': {'pos1': None, 'pos2': None},
                'the_end':    {'pos1': None, 'pos2': None},
            }



        zips = [x for x in os.listdir(self.reg_bkps_dir) if x.endswith('.zip')]

        if self.server.is_command(message, 'mdhelp'):
            self.server.show_command(player, 'rb help'           , 'Muestra los comandos del regional backup.')

        elif self.server.is_command(message, 'rb help'):
            self.server.show_command(player, 'rb clear'          , 'Limpia tu lista.')
            self.server.show_command(player, 'rb list'           , 'Muestra tu lista de regiones.')
            self.server.show_command(player, 'rb add'            , 'Añade a tu lista una región.')
            self.server.show_command(player, 'rb remove'         , 'Quita de tu lista la región donde te encuentras actualmente.')
            self.server.show_command(player, 'rb pos1'       , 'Establece la primera esquina de un rectángulo de regiones.')
            self.server.show_command(player, 'rb pos2'       , 'Establece la segunda esquina de un rectángulo de regions.')
            self.server.show_command(player, 'rb del <index>'    , 'Elimina la región de índice <index> de tu lista.')
            self.server.show_command(player, 'rb mk-bkp <name>'  , 'Crea un reg-bkp <name>.zip con las regiones añadidas.')
            self.server.show_command(player, 'rb update <name>'  , 'Actualiza el reg-bkp <name>.zip reimportando regiones.')
            self.server.show_command(player, 'rb bkps'           , 'Lista los backups creados.')
            
            if not self.is_admin_or_whitelisted(player) and self.server.name == 'SMP': return
            self.server.show_command(player, 'rb load-bkp <name>', 'Carga el reg-bkp <name>.zip.')
            self.server.show_command(player, 'rb del-bkp <name>' , 'Elimina el reg-bkp <name>.zip.')
            self.server.show_command(player, 'rb confirm'        , 'Confirma la carga del reg-bkp específicado.')
            
            if player in self.server.admins:
                self.server.show_command(player, 'rb wl list'            , 'Muestra la whitelist de carga de reg-bkps.')
                self.server.show_command(player, 'rb wl add <player>'    , 'Añade un jugador a la whitelist.')
                self.server.show_command(player, 'rb wl remove <player>' , 'Quita un jugador de la whitelist.')
                self.server.show_command(player, 'rb wl clear'           , 'Limpia toda la whitelist.')

        elif self.server.is_command(message, 'rb add'):
            pos, dim = await self.get_player_position(player)
            reg = self.pos_to_region(pos)

            if reg not in self.files_to_zip[player][dim]:
                self.files_to_zip[player][dim].append(reg)

            self.show_list(player)
        
        elif self.server.is_command(message, 'rb remove'):
            pos, dim = await self.get_player_position(player)
            current_reg = self.pos_to_region(pos)
            if current_reg in self.files_to_zip[player][dim]:
                self.files_to_zip[player][dim].remove(current_reg)
                self.server.send_response(player, f'✔ Región {current_reg} eliminada de tu lista.')
            else:
                self.server.send_response(player, '✖ La región actual no está en tu lista.')
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
            self.files_to_zip[player] = {'overworld': [], 'the_nether': [], 'the_end': []}
            self.player_positions[player] = {'pos1': None, 'pos2': None}
            self.show_list(player)
        
        elif self.server.is_command(message, 'rb pos1'):
            pos, dim = await self.get_player_position(player)
            self.player_positions[player][dim]['pos1'] = pos
            self.server.send_response(player, f"✔ Pos1 establecida")
            
            if self.player_positions[player][dim]['pos2']:
                self.add_rect_regions(player, dim)
                self.show_list(player)

        elif self.server.is_command(message, 'rb pos2'):
            pos, dim = await self.get_player_position(player)

            self.player_positions[player][dim]['pos2'] = pos
            self.server.send_response(player, f"✔ Pos2 establecida")

            if self.player_positions[player][dim]['pos1']:
                self.add_rect_regions(player, dim)
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
            zip_path = os.path.join(self.reg_bkps_dir, f'{name}.zip')

            if not name or not name + '.zip' in zips:
                self.server.send_response(player, '✖ Debes proveer un nombre en la lista.')
                return
            
            # Leer autor del backup
            author = None
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                if 'bkp_log.txt' in zip_ref.namelist():
                    lines = zip_ref.read('bkp_log.txt').decode().split('\n')
                    if lines:
                        author_line = lines[0]
                        if author_line.startswith("Backup realizado por:"):
                            author = author_line.removeprefix("Backup realizado por:").strip()

            # Verificar permisos
            if not self.is_admin_or_whitelisted(player):
                if author is None:
                    self.server.send_response(player, '✖ No se puede actualizar: backup sin autor registrado.')
                    return
                elif player != author:
                    self.server.send_response(player, '✖ Solo los administradores o el creador del backup puede actualizarlo.')
                    return

            if self.creating_bkp: 
                self.server.send_response(player, '✖ Alguien más está creando un backup ahorita.')
                return

            self.creating_bkp = True
            await self.update_reg_bkp(player, name)


        elif not self.is_admin_or_whitelisted(player) and self.server.name == 'SMP': return

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
            zip_name = message.removeprefix(f'{self.server.prefix}rb del-bkp').strip()
            zip_file = zip_name + '.zip'
            zip_path = os.path.join(self.reg_bkps_dir, zip_file)

            if zip_file not in [x for x in os.listdir(self.reg_bkps_dir) if x.endswith('.zip')]:
                self.server.send_response(player, '✖ No hay un reg-bkp con ese nombre.')
                return

            # Leer autor del backup
            author = None
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                if 'bkp_log.txt' in zip_ref.namelist():
                    lines = zip_ref.read('bkp_log.txt').decode().split('\n')
                    if lines and lines[0].startswith("Backup realizado por:"):
                        author = lines[0].removeprefix("Backup realizado por:").strip()

            # Verificar permisos
            if not self.is_admin_or_whitelisted(player):
                if author is None:
                    self.server.send_response(player, '✖ No se puede eliminar: backup sin autor registrado.')
                    return
                elif player != author:
                    self.server.send_response(player, '✖ Solo el creador o un admin puede eliminar este backup.')
                    return

            # Borrar backup
            os.remove(zip_path)
            self.show_bkps(player)
            self.server.send_response(player, f'✔ reg-bkp {zip_file} eliminado.')

        elif not player in self.server.admins or self.server.name != 'SMP': return

        elif self.server.is_command(message, 'rb wl list'):
            self.show_whitelist(player)

        elif self.server.is_command(message, 'rb wl add'):
            target = message.removeprefix(f'{self.server.prefix}rb wl add').strip()
            if not target:
                self.server.send_response(player, '✖ Debes proveer un jugador.')
                return

            self.whitelisted_players.add(target)
            self.save_whitelist()
            self.server.send_response(player, f'✔ {target} agregado a la whitelist.')
            self.show_whitelist(player)

        elif self.server.is_command(message, 'rb wl remove'):
            target = message.removeprefix(f'{self.server.prefix}rb wl remove').strip()
            if not target:
                self.server.send_response(player, '✖ Debes proveer un jugador.')
                return

            if target in self.whitelisted_players:
                self.whitelisted_players.remove(target)
                self.save_whitelist()
                self.server.send_response(player, f'✔ {target} removido de la whitelist.')
            else:
                self.server.send_response(player, f'✖ {target} no está en la whitelist.')
            self.show_whitelist(player)

        elif self.server.is_command(message, 'rb wl clear'):
            self.whitelisted_players.clear()
            self.save_whitelist()
            self.server.send_response(player, '✔ Whitelist limpiada.')


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
                        
                        if os.path.exists(file_path):
                            zipf.write(file_path, os.path.join(folder, reg))
                        
                    log_content.append(f'{dim} : {reg}')

            log_text = f"Backup realizado por: {player}\nArchivos respaldados:\n" + "\n".join(log_content)
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
                raw_lines = zip_ref.read('bkp_log.txt').decode().split('\n')

                log_info = []
                for line in raw_lines:
                    if ' : r.' in line and line.endswith('.mca'):
                        log_info.append(line)
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
                        
                        if os.path.exists(file_path):
                            zipf.write(file_path, os.path.join(folder, reg))
                        
                    log_content.append(f'{dim} : {reg}')

            log_text = f"Backup realizado por: {player}\nArchivos respaldados:\n" + "\n".join(log_content)
            zipf.writestr("bkp_log.txt", log_text)

        self.server.execute('save-on')
        self.server.send_response(player, f'✔ reg-bkp {name}.zip actualizado.')
        self.server.add_log(f'reg-bkp {name}.zip updated')
        self.creating_bkp = False

    def         is_admin_or_whitelisted(self, player: str):
        return player in self.server.admins or player in self.whitelisted_players

    def         show_whitelist(self, player: str):
        if not self.whitelisted_players:
            self.server.send_response(player, 'Whitelist vacía.')
            return

        msg = ['Whitelist de reg-bkps:']
        for i, whitelisted in enumerate(sorted(self.whitelisted_players), start=1):
            msg.append(f'{i} • {whitelisted}')
        self.server.send_response(player, msg)
        
    def         load_whitelist(self):
        players = read_file(self.whitelist_text_path).strip().split("\n")
        return set(player for player in players if player)

    def         save_whitelist(self):
        write_in_file(self.whitelist_text_path, "\n".join(sorted(self.whitelisted_players)))


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
                    log_info_lines = zip_ref.read('bkp_log.txt').decode().split('\n')
                    if len(log_info_lines) > 2:
                        author = log_info_lines[0].removeprefix("Backup realizado por: ").strip()
                        regions_log = ' | '.join(log_info_lines[2:])
                        log_info = f"Hecho por: {author} | {regions_log}"
                    elif len(log_info_lines) > 1:
                        author = log_info_lines[0].removeprefix("Backup realizado por: ").strip()
                        log_info = f"Hecho por: {author}"
                    else:
                        log_info = 'Sin registro de autor.'
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
    
    
    async def get_player_position(self, player: str):
        # Obtener posición
        raw_pos = await self.server.get_data(player, 'Pos')
        raw_pos = raw_pos[raw_pos.find('[')+1 : raw_pos.find(']')].split(',')
        pos = tuple(float(x.strip()[:-1]) for x in raw_pos)

        # Obtener dimensión
        raw_dim = await self.server.get_data(player, 'Dimension')
        dim = raw_dim.replace('"','').split(':')[1]

        return pos, dim
    
    def get_region_folder(self, dim: str):
        base = os.path.join(self.server.path_files, 'server', 'world')

        if dim == 'overworld':
            return os.path.join(base, 'region')
        elif dim == 'the_nether':
            return os.path.join(base, 'DIM-1', 'region')
        elif dim == 'the_end':
            return os.path.join(base, 'DIM1', 'region')
        else:
            raise ValueError(f'Dimensión desconocida: {dim}')

    def add_rect_regions(self, player: str, dim: str):
        pos1 = self.player_positions[player][dim]['pos1']
        pos2 = self.player_positions[player][dim]['pos2']
        if not pos1 or not pos2:
            return

        x_min, x_max = sorted([pos1[0], pos2[0]])
        z_min, z_max = sorted([pos1[2], pos2[2]])

        self.files_to_zip[player][dim] = []

        region_folder = self.get_region_folder(dim)

        for reg_file in os.listdir(region_folder):
            if not reg_file.endswith('.mca'):
                continue

            r_x, r_z = map(int, reg_file[2:-4].split('.'))

            reg_x_min = r_x * 512
            reg_x_max = reg_x_min + 511
            reg_z_min = r_z * 512
            reg_z_max = reg_z_min + 511

            if not (reg_x_max < x_min or reg_x_min > x_max or reg_z_max < z_min or reg_z_min > z_max):
                self.files_to_zip[player][dim].append(reg_file)

