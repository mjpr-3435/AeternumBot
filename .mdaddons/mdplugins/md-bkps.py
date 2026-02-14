import asyncio
import threading
import shutil
import os

from datetime import datetime
from mcdis_rcon.utils import hover_and_suggest, extras, sct, hover
from Classes.AeServer import AeServer

class mdplugin():
    def __init__(self, server: AeServer):
        self.server = server
        self.scheduled_load_backup  = {}
        self.action_confirmed       = False
        self.creating_backup        = False

    async def   on_player_command(self, player: str, message: str):
        backups = [x for x in os.listdir(self.server.path_bkps)]

        
        if self.server.is_command(message, 'mdhelp'):
            self.server.show_command(player, 'bk help | bk'             , 'Muestra los comandos del backup manager.')

        elif self.server.is_command(message, 'bk') or self.server.is_command(message, 'bk help'):
            self.server.show_command(player, 'bkps'             , 'Lista los backups del servidor.')
            self.server.show_command(player, 'mk-bkp <comment | default : None>' , 'Crea un backup.')
            if not player in self.server.admins: return

            self.server.show_command(player, 'del-bkp <name>'   , 'Elimina el backup <name>.')
            self.server.show_command(player, 'load-bkp <name>'  , 'Carga el backup <name>.')
            self.server.show_command(player, 'bk confirm'       , 'Confirma la acción solicitada.')
        
        elif self.server.is_command(message, 'bkps'):
            self.show_bkps(player)
    
        elif self.server.is_command(message, 'mk-bkp'):
            comment = message.removeprefix(f'{self.server.prefix}mk-bkp').strip()
            if self.creating_backup:
                await self.server.send_response(player, '✖ Alguien más está creando un backup ahorita.')
                return
            
            await self.make_bkp(player, comment if comment else None)
        
        if not player in self.server.admins:
            return
        
        elif self.server.is_command(message, 'load-bkp'):
            backup = message.removeprefix(f'{self.server.prefix}load-bkp').strip()

            if backup in backups:
                self.scheduled_load_backup[player]  = backup

                dummy = extras(
                [hover_and_suggest('!!bk confirm' , color= 'gray', suggest = '!!bk confirm', hover = '!!bk confirm')],
                text = f"Para confirmar la carga de §d[{backup}]§7 utiliza "
                )

                self.server.execute(f'tellraw {player} {dummy}')

            else:
                self.server.send_response(player, '✖ No hay un backup con ese nombre.')

        elif self.server.is_command(message, 'bk confirm'):
            if not player in self.scheduled_load_backup.keys(): 
                self.server.send_response(player, '✖ No has solicitado la carga o creación de ningún backup.')
                return
            
            elif self.action_confirmed: 
                self.server.send_response(player, '✖ Ya alguien más confirmó la carga o creación de un backup.')
                return
            
            self.action_confirmed = True

            for i in range(5):
                await asyncio.sleep(1)
                self.server.send_response('@a', f'El servidor se reiniciará en {5-i} segundos.')

            if player in self.scheduled_load_backup.keys():
                await self.load_bkp(player)

        elif self.server.is_command(message, 'del-bkp'):
            backup = message.removeprefix(f'{self.server.prefix}del-bkp').strip()

            if backup in backups:
                shutil.rmtree(os.path.join(self.server.path_bkps, backup))
                self.server.send_response(player, f'✔ Backup {backup} eliminado.')

                self.show_bkps(player)
            else:
                self.server.send_response(player, '✖ No hay un backup con ese nombre.')

    async def   listener_events(self, log : str):
        if not 'INFO]:' in log: 
            pass
            
        elif log.endswith('Saved the game') and self.waiting:
                self.waiting = False

    async def   load_bkp (self, player: str):
        zip = self.scheduled_load_backup[player]

        self.server.stop()

        while self.server.is_running():
            await asyncio.sleep(0.1)
            
        discord_message = await self.server.send_to_console(f'Unpacking the backup {zip}...')

        counter = [0,0]
        reports = {'error': False}
        
        unpack_bkp = self.server.client.error_wrapper(
            error_title = f'{self.server.name}: unpack_bkp()',
            reports = reports
            )(self.server.unpack_bkp)

        task = threading.Thread(
            target = unpack_bkp, 
            args = (zip,),
            kwargs = {'counter' : counter})
        task.start()
        
        while task.is_alive():
            if counter[1] == 0: 
                await asyncio.sleep(0.1)
            else:
                show = '```md\n[md-bkps]: [{}/{}] files have been unpacked...\n```'\
                    .format(counter[0], counter[1])
                await discord_message.edit(
                    content = show)
                await asyncio.sleep(0.5)
        
        if reports['error']:
            msg = '```md\n[md-bkps]: ✖ An error occurred while unpacking files.\n```'
        else:
            msg = '```md\n[md-bkps]: ✔ The files have been successfully unpacked.\n```'

        await discord_message.edit(content = msg)

        self.server.start()
    
    async def make_bkp(self, player, comment = None):
        self.creating_backup = True

        discord_message = await self.server.send_to_console('Creating backup...')

        self.waiting = True

        self.server.execute('save-off')
        self.server.execute('save-all')

        while self.waiting:
            await asyncio.sleep(1)

        self.server.execute(f'tellraw @a {{"text":"[md-bkps]: Creando backup...", "color": "gray"}}')

        counter = [0,0]
        reports = {'error': False}
        
        make_bkp = self.server.client.error_wrapper(
            error_title = f'{self.server.name}: make_bkp()',
            reports = reports
            )(self.server.make_bkp)

        limit = self.server.client.config['Backups']
        all_backups = [
            x for x in os.listdir(self.server.path_bkps)
            if os.path.isdir(os.path.join(self.server.path_bkps, x))
        ]

        if len(all_backups) >= limit:
            metadata = []

            for b in all_backups:
                log_file = os.path.join(self.server.path_bkps, b, 'backup_log.txt')
                author = None
                date = None

                if os.path.exists(log_file):
                    with open(log_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            if line.startswith('Backup created on:'):
                                date = datetime.strptime(
                                    line.replace('Backup created on:', '').strip(),
                                    '%Y-%m-%d %H:%M:%S'
                                )
                            elif line.startswith('Backup created by:'):
                                author = line.replace('Backup created by:', '').strip()

                is_admin = (author is None) or (author in self.server.admins)

                metadata.append({
                    'name': b,
                    'date': date,
                    'author': author,
                    'is_admin': is_admin
                })

            admin_backups = [m for m in metadata if m['is_admin']]

            if admin_backups:
                latest_admin = max(admin_backups, key=lambda x: x['date'])

                ordered = sorted(metadata, key=lambda x: x['date'])

                candidates = [m for m in ordered if m['name'] != latest_admin['name']]

                if candidates:
                    oldest = candidates[0]
                    shutil.rmtree(os.path.join(self.server.path_bkps, oldest['name']))

        task = threading.Thread(
            target = make_bkp, 
            kwargs = {'counter' : counter,
                      'Force': True})
        task.start()
        
        while task.is_alive():
            if counter[1] == 0: 
                await asyncio.sleep(0.1)
            else:
                show = '```md\n[md-bkps]: [{}/{}] files have been copying...\n```'\
                    .format(counter[0], counter[1])
                
                percent = counter[0]*100/counter[1]
                self.server.execute(f'tellraw @a {{"text":"[md-bkps]: {sct["c:white"]}{percent:6.2f}{sct["c:gold"]}%{sct["f:reset"]} archivos copiados...", "color": "gray"}}')

                await discord_message.edit(
                    content = show)
                await asyncio.sleep(1)
        
        self.server.execute('save-on')

        if reports['error']:
            msg = '```md\n[md-bkps]: ✖ An error occurred while copying files.\n```'
            self.server.execute(f'tellraw @a {{"text":"[md-bkps]: Ocurrio un error mientras se copiaban los archivos.", "color": "gray"}}')
        else:
            backups = sorted(
                os.listdir(self.server.path_bkps),
                key=lambda x: os.path.getmtime(os.path.join(self.server.path_bkps, x))
            )
            last_backup = backups[-1]
            log_path = os.path.join(self.server.path_bkps, last_backup, 'backup_log.txt')

            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(f'Backup created by: {player}\n')
                if comment:
                    f.write(f'Comment: {comment}\n')


            msg = '```md\n[md-bkps]: ✔ The backup have been successfully created.\n```'
            self.server.execute(f'tellraw @a {{"text":"[md-bkps]: El backup se creo exitosamente.", "color": "gray"}}')

        await discord_message.edit(content = msg)
        self.creating_backup = False
        
    def         show_bkps(self, player : str):
        backups = [x for x in os.listdir(self.server.path_bkps)]
        backups.sort()
        
        if not backups:
            self.server.send_response(player, 'No se han creado backups.')
            return
        
        self.server.send_response(player, 'Backups disponibles:')

        for backup in backups:
            file = os.path.join(self.server.path_bkps, backup, 'backup_log.txt')

            if os.path.exists(file):
                date = "Date not found in log"
                comment = None
                author = None

                with open(file, 'r', encoding='utf-8') as log_file:
                    lines = log_file.read().splitlines()
                    for line in lines:
                        if line.startswith('Backup created on:'):
                            date_str = line.replace('Backup created on:', '').strip()
                            date = datetime.strptime(
                                date_str,
                                '%Y-%m-%d %H:%M:%S'
                            ).strftime('%Y-%m-%d %H:%M:%S')

                        elif line.startswith('Backup created by:'):
                            author = line.replace('Backup created by:', '').strip()

                        elif line.startswith('Comment:'):
                            comment = line.replace('Comment:', '').strip()
            else:
                date = "Date not found in log"
                comment = None
                author = None

            dummy = [
                hover_and_suggest('[>] ', color='green', suggest=f'!!load-bkp {backup.removesuffix(".zip")}', hover='Load backup'),
                hover_and_suggest('[x] ', color='red', suggest=f'!!del-bkp {backup.removesuffix(".zip")}', hover='Del backup'),
                f'{{"text":"{backup} ","color":"white"}}',
                f'{{"text":"[{date}] ","color":"gray"}}'
            ] + (
                [f'{{"text":"by {author} ","color":"dark_aqua"}}'] if author else []
            ) + (
                [hover('[C]', color='gold', hover=comment)] if comment else []
            )

            self.server.execute(f'tellraw {player} {extras(dummy)}')
