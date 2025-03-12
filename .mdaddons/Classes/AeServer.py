from mcdis_rcon.classes import Server, McDisClient
from mcdis_rcon.utils import write_in_file, read_file
import asyncio
import re
import os

class AeServer(Server):
    def         __init__                (self, name: str, client: McDisClient, config: dict):
        super().__init__(name, client, config)

        self.admins                     = ['KassiuLo', 'LuisitoLapapa', 'XMasi', 'NajaHorse']
        self.omit_crash_report_relay    = False
        self.stop_signal_received       = False
        self.online_players             = []
        self.bots                       = []
        self.requested_data             = {}


        self.players_text_path      = os.path.join(self.path_plugins, 'logger', 'players_log.txt')
        self.bots_text_path         = os.path.join(self.path_plugins, 'logger', 'bots_log.txt')

        os.makedirs(os.path.join(self.path_plugins, 'logger'), exist_ok = True)
        if not os.path.exists(self.players_text_path): write_in_file(self.players_text_path, '')
        if not os.path.exists(self.bots_text_path): write_in_file(self.bots_text_path, '')

    async def   get_data                (self, player: str, data: str):
        self.requested_data[player] = None
        self.execute(f"data get entity {player} {data}")
        
        while not self.requested_data[player]:
            await asyncio.sleep(0.01)
        
        return self.requested_data.pop(player)
    
    async def   _listener_events        (self, log : str):
        if 'INFO]: ' in log:
            if any([f'<{player}>' in log for player in self.online_players]):
                player = log[log.index('<') + 1:log.index('>')]
                message = log[log.index('>') + 1:].strip()

                await self.call_plugins('on_player_message', (player, message))
                
                if not message.startswith(self.prefix): return
                
                await self.call_plugins('on_player_command', (player, message))

            elif 'logged in with entity id' in log:
                match = re.search(r"(.*?) logged in with entity id", log)
                player_and_ip = match.group(1).strip().split(' ')[-1]
                player = player_and_ip.split('[')[0]
                local = player_and_ip.removeprefix(player) == '[local]'
                
                if local:
                    self.bots.append(player)
                    self.add_bot_log(player)
                else:
                    self.online_players.append(player)
                    self.add_player_log(player)

                await self.call_plugins('on_player_join', (player,))
        
            elif log.endswith('left the game'):
                match = re.search(r"(.*?) left the game", log)
                formated_player = match.group(1).strip().split(' ')[-1]
                player = next(filter(lambda x: x == formated_player, self.bots + self.online_players), None)
                
                if player in self.bots: self.bots.remove(player)
                elif player in self.online_players: self.online_players.remove(player)

                await self.call_plugins('on_player_left', (player,))

            elif 'Starting minecraft server' in log:
                self.bots = []
                self.online_players = []
                await self.call_plugins('on_started')

            elif log.endswith('For help, type "help"'):
                await self.call_plugins('on_already_started')
                
            elif log.endswith('Stopping server'):
                self.stop_signal_received = True
                await self.call_plugins('on_stopped')
            
            elif log.endswith('ThreadedAnvilChunkStorage: All dimensions are saved') and self.stop_signal_received:
                self.bots = []
                self.online_players = []
                self.stop_signal_received = False
                await self.call_plugins('on_already_stopped')

            elif any(f'{x} has the following entity data' in log for x in self.requested_data.keys()):
                match = re.search(r"(.*?) has the following entity data: (.*)", log)
                player = match.group(1).strip().split(' ')[-1]
                data = match.group(2)

                self.requested_data[player] = data

        elif 'ERROR]: ' in log:
            if  log.endswith('Considering it to be crashed, server will forcibly shutdown.'): 
                if self.omit_crash_report_relay:
                    self.stop_relaying(self.log_format('Crash detected. Finalizing relay...'))
                
                await self.call_plugins('on_crash') 

        await self.call_plugins('listener_events', (log,))

    def         add_player_log          (self, player : str):
        players = read_file(self.players_text_path).strip().split('\n')
        bots = read_file(self.bots_text_path).strip().split('\n')
        
        if player in bots:
            bots.remove(player)
            write_in_file(self.bots_text_path, bots)

        if player in players: return
        
        write_in_file(self.players_text_path, '\n'.join(players + [player]))
    
    def         add_bot_log             (self, bot : str):
        players = read_file(self.players_text_path).strip().split('\n')
        bots = read_file(self.bots_text_path).strip().split('\n')
        
        if bot in players:
            players.remove(bot)
            write_in_file(self.players_text_path, players)

        if bot in bots: return

        write_in_file(self.bots_text_path, '\n'.join(bots + [bot]))

    def         get_player_log          (self):
        players = read_file(self.players_text_path).strip().split('\n')

        return players

    def         get_bot_log             (self):
        bots = read_file(self.bots_text_path).strip().split('\n') 

        return bots
