import discord
import asyncio

from Classes.AeServer import AeServer

class mdplugin():
    def __init__(self, server: AeServer):
        self.server                     = server
        self.webhook : discord.Webhook  = None
        self.chatbrige_id               = 930324106455416883

        asyncio.create_task(self.load())

    async def load(self):
        channel = self.server.client.get_channel(self.chatbrige_id)
        name = "ChatBridge"

        webhooks = await channel.webhooks()

        for webhook in webhooks:
            if webhook.name == name:
                self.webhook = webhook
                return
        
        # self.webhook = channel.create_webhook(name=name)

    async def listener_on_message   (self, message: discord.Message):
        if self.webhook == None: return

        elif message.author.bot : return

        elif message.channel.id == self.webhook.channel.id:
            if not (self.server.online_players + self.server.bots): return

            msg = message.content.replace('\n', ' ').replace('"',"'")
            self.server.send_response('@a', f'[DIS] <{message.author.display_name}> {msg}')

    async def on_player_message     (self, player: str, message: str):

        if self.webhook == None: return
    
        self.send_to_servers(f'[{self.server.name}] <{player}> {message}')
            
        await self.webhook.send(f'{message}', username = f'[{self.server.name}] {player}', avatar_url = f'https://mc-heads.net/head/{player.lower()}.png')

    async def on_player_join        (self, player: str):
        if self.webhook == None: return

        self.send_to_servers(f'[{self.server.name}] {player} ha entrado al servidor')
            
        await self.webhook.send(f'[{self.server.name}] {player} ha entrado al servidor')
            
    async def on_player_left        (self, player: str):
        if self.webhook == None: return

        self.send_to_servers(f'[{self.server.name}] {player} ha salido del servidor')
            
        await self.webhook.send(f'[{self.server.name}] {player} ha salido del servidor')

    async def on_already_started    (self):
        if self.webhook == None: return

        self.send_to_servers(f'[{self.server.name}] Servidor abierto!')
            
        await self.webhook.send(f'[{self.server.name}] Servidor abierto!')

    async def on_stopped            (self):
        if self.webhook == None: return

        self.send_to_servers(f'[{self.server.name}] Servidor detenido')
            
        await self.webhook.send(f'[{self.server.name}] Servidor detenido')

    async def on_crash              (self):
        if self.webhook == None: return

        self.send_to_servers(f'[{self.server.name}] El servidor crasheó')
            
        await self.webhook.send(f'[{self.server.name}] El servidor crasheó')

    def send_to_servers(self, msg: str):
        msg = msg.replace("\n","").replace('"',"'")

        for server in self.server.client.servers:
            if server.name != self.server.name and (server.online_players + server.bots):
                server.send_response('@a', msg) 
