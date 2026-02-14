import asyncio
import threading
import shutil
import os

from datetime import datetime
from mcdis_rcon.utils import hover_and_suggest, extras, sct
from Classes.AeServer import AeServer

class mdplugin():
    def __init__(self, server: AeServer):
        self.server = server
        self.scheduled_load_backup  = {}
        self.action_confirmed       = False

    async def   on_player_command(self, player: str, message: str):
        backups = [x for x in os.listdir(self.server.path_bkps)]

        if not player in self.server.admins:
            return
        
        elif self.server.is_command(message, 'mdhelp'):
            self.server.show_command(player, 'bk'             , 'Muestra los comandos del backup manager.')

        elif self.server.is_command(message, 'bk help'):
            self.server.show_command(player, 'bkps'             , 'Lista los backups del servidor.')
            self.server.show_command(player, 'mk-bkp'           , 'Crea un backup con la lógica de McDis.')
            self.server.show_command(player, 'del-bkp <name>'   , 'Elimina el backup <name>.zip.')
            self.server.show_command(player, 'load-bkp <name>'  , 'Carga el backup <name>.zip.')
            self.server.show_command(player, 'bk confirm'          , 'Confirma la acción solicitada.')
        
        elif self.server.is_command(message, 'bkps'):
            self.show_bkps(player)
    
        elif self.server.is_command(message, 'mk-bkp'):
            await self.make_bkp(player)

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
                self.show_bkps(player)
                self.server.send_response(player, f'✔ Backup {backup} eliminado.')
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

    async def   make_bkp (self, player):
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
            msg = '```md\n[md-bkps]: ✔ The backup have been successfully created.\n```'
            self.server.execute(f'tellraw @a {{"text":"[md-bkps]: El backup se creo exitosamente.", "color": "gray"}}')

        await discord_message.edit(content = msg)
        
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
                with open(file, 'r', encoding='utf-8') as log_file:
                    lines = log_file.read().splitlines()
                    for line in lines:
                        if line.startswith('Backup created on:'):
                            date_str = line.replace('Backup created on:', '').strip()
                            date = datetime.strptime(
                                date_str,
                                '%Y-%m-%d %H:%M:%S'
                            ).strftime('%Y-%m-%d %H:%M:%S')
                            break
            else:
                date = "Date not found in log"

            dummy = [
            hover_and_suggest('[>] ' , color = 'green', suggest = f'!!bk load-bkp {backup.removesuffix(".zip")}', hover = 'Load backup'),
            hover_and_suggest('[x] ' , color = 'red', suggest = f'!!bk del-bkp {backup.removesuffix(".zip")}', hover = 'Del backup'),
            f'{{"text":"{backup} [{date}]"}}'
            ]

            self.server.execute(f'tellraw {player} {extras(dummy)}')