from Classes.AeServer import AeServer
from mcdis_rcon.utils import hover_and_suggest, sct

import discord
import asyncio

class mdplugin():
    def __init__(self, server: AeServer):
        self.server                     = server
        self.tts_id                     = 914536283781615636
        self.guild_id                   = 839325517529612348
        self.channel                    = self.server.client.get_channel(self.tts_id)
        self.guild                      = self.server.client.get_guild(self.guild_id)
        self.active_players             = []

        asyncio.create_task(self.load())

    async def load(self):
        name = "TTs Extra"

        webhooks = await self.channel.webhooks()

        for webhook in webhooks:
            if webhook.name == name:
                self.webhook = webhook
                return

    async def   on_player_command     (self, player: str, message: str):
        if self.server.is_command(message, 'mdhelp'):
            self.server.show_command(player, "tts", "Todos tus mensajes serán enviados al canal.")
        
        elif self.server.is_command(message, 'tts'):
            if player in self.active_players:
                self.active_players.remove(player)

                self.server.send_response(player, f'§8@{player} §7-> §c[Desuscrito]')
                return
            
            self.active_players.append(player)
            self.server.send_response(player, f'§8@{player} §7-> §a[Suscrito]')
    
    async def on_player_message(self, player: str, message: str):
        if player in self.active_players and not message.startswith('!!'):
            await self.webhook.send(f'{message}', username = f'{player}', avatar_url = f'https://mc-heads.net/head/{player.lower()}.png')

    async def on_player_left        (self, player: str):
        if player in self.active_players:
                self.active_players.remove(player)
