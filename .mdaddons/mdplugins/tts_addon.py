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
            # self.server.show_command(player, 'md tts', 'Muestra los comandos para usar los tts.')

        elif False and self.server.is_command(message, 'md tts'):
            self.server.show_command(player, "tts", "Todos tus mensajes serán enviados al canal.")
            self.server.show_command(player, "tts-join" , "Muestra todos los canales de voz del servidor.")
            self.server.show_command(player, "tts-disconnect" , "Desconectar al bot del canal de voz.")
        
        elif self.server.is_command(message, 'tts'):
            if player in self.active_players:
                self.active_players.remove(player)

                self.server.send_response(player, f'§8@{player} §7-> §c[Desuscrito]')
                return
            
            self.active_players.append(player)
            self.server.send_response(player, f'§8@{player} §7-> §a[Suscrito]')

        elif False and self.server.is_command(message, 'tts-join'):
            voice_channel_name = message.removeprefix(f'{self.server.prefix}tts-join').strip()

            if not voice_channel_name:
                for voice_channel in self.guild.voice_channels:
                    msg = hover_and_suggest(f'• {voice_channel.name}', suggest = f'!!tts-join {voice_channel.name}', hover = f'!!tts-join {voice_channel.name}')
                    self.server.execute(f'tellraw {player} {msg}')
                return

            proceed = await self.connect_to(voice_channel_name)

            if proceed:
                self.server.send_response(player, '✔ Bot conectado.')
            else:
                self.server.send_response(player, '✖ Canal no encontrado.')

        elif False and self.server.is_command(message, 'tts-disconnect'):
            voice_client = discord.utils.get(self.server.client.voice_clients, guild=self.guild)

            if voice_client is None:
                self.server.send_response(player, '✖ El bot no estaba conectado a ningún canal.')
                return
            
            await voice_client.disconnect()
            self.server.send_response(player, '✔ Bot desconectado.')
            
    async def   on_player_message(self, player: str, message: str):
        if player in self.active_players and not message.startswith('!!'):
            await self.webhook.send(f'{message}', username = f'{player}', avatar_url = f'https://mc-heads.net/head/{player.lower()}.png')

    async def on_player_left        (self, player: str):
        if player in self.active_players:
                self.active_players.remove(player)

    async def connect_to (self, voice_channel_name):
        voice_channel = discord.utils.get(self.guild.voice_channels, name = voice_channel_name)
        voice_client = discord.utils.get(self.server.client.voice_clients, guild=self.guild)

        if not voice_channel:
            return False

        if voice_client:
            await voice_client.disconnect()
            await voice_channel.connect()
        else:
            await voice_channel.connect()

        return True
