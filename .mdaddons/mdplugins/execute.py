import os
import asyncio

from mcdis_rcon.utils import extras, hover_and_suggest, read_yml, sct, truncate, hover
from Classes.AeServer import AeServer

class mdplugin():
    def __init__(self, server: AeServer):
        self.server = server
        self.config = {"MobSwitch" : "Reset"}
        self.running = []

    async def on_already_started    (self):
        await asyncio.sleep(5)

        keys = list(self.config.keys())

        for key in keys:
            path = os.path.join(self.server.path_commands, f'{key}.yml')
            if not os.path.exists(path): continue
                                
            data = read_yml(path)
            commands = data[self.config[key]]   
            
            for command in commands:
                if 'await' in command:
                    await asyncio.sleep(int(command.replace('await','').strip()))
                    continue
                self.server.execute(command.strip())
                await asyncio.sleep(1)

    async def on_player_command     (self, player: str, message: str):
        commands = [file.removesuffix('.yml') for file in os.listdir(self.server.path_commands) if file.endswith('.yml')]
        commands.sort()
        raw_message = message
        message = message.replace(' ', '').lower()

        if self.server.is_command(raw_message, 'mdhelp'):
            self.server.show_command(player, 
                            "commands", 
                            "Lista de comandos predifinidos del servidor.")
            
        elif self.server.is_command(message, 'commands'):
            if not commands:
                self.server.send_response(player, "No hay comandos disponibles.")
                return
            
            self.server.send_response(player, "Comandos disponibles:")
            for i in range(len(commands)):
                text = f'• {commands[i]}'
                path = os.path.join(self.server.path_commands, f'{commands[i]}.yml')

                data = read_yml(path)
                keys = list(data.keys())
                
                placeholder = 'Acciones: ' + ', '.join(keys[1:])
                ext = extras([hover_and_suggest(text, suggest = self.server.prefix + commands[i] + ' ', hover = placeholder)])
                self.server.execute(f'tellraw {player} {ext}')

        elif any(message.startswith(self.server.prefix + command.replace(' ', '').lower()) for command in commands):
            command = next(filter(lambda command: message.startswith(self.server.prefix + command.replace(' ', '').lower()), commands), None)
            action = message.removeprefix(self.server.prefix + command.replace(' ', '').lower())

            if not command: return
            path = os.path.join(self.server.path_commands, f'{command}.yml')
            data = read_yml(path)
            keys = list(data.keys())

            if not action:
                messages = [f"Descripción: {data[keys[0]]}", " ", "Acciones disponibles:"]
                self.server.send_response(player, messages)

                for i in range(1, len(keys)):
                    commands = ', '.join(data[keys[i]])
                    suggestion = self.server.prefix + command + ' ' + keys[i]
                    ext = extras([hover_and_suggest(f'• {keys[i]}', suggest =  suggestion, hover = commands)])
                    self.server.execute(f'tellraw {player} {ext}')
                return
            

            if action.lower().replace(' ','') in [action.lower().replace(' ','') for action in keys]:
                action = next(filter(lambda x: x.lower().replace(' ','') == action.lower().replace(' ',''), keys))
                
                if f'{command}:{action}' in self.running:
                    self.server.send_response(player, '✖ Alguien ya está ejecutando este comando.')
                    return
                
                commands = data[action]   
                self.server.send_response(player, 'Ejecutando comandos...')
                self.running.append(f'{command}:{action}')
                
                for cmd in commands:
                    cmd_log = extras(text = '• Ejecutando ', extras = [hover(text = f'[{truncate(cmd,30)}].', color = 'dark_gray', hover = cmd)])
                    self.server.execute(f'tellraw {player} {cmd_log}')

                    if 'await' in cmd:
                        await asyncio.sleep(int(cmd.replace('await','').strip()))
                        continue
                    self.server.execute(cmd.strip())
                    await asyncio.sleep(1)

                self.running.remove(f'{command}:{action}')

                self.server.send_response(player, f'✔ {command}: Comandos ejecutados.')

            else:
                self.server.send_response(player, '✖ No hay una acción con ese nombre.')