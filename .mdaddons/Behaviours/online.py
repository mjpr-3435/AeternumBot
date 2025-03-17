from mcdis_rcon.classes import McDisClient
from Classes.AeServer import AeServer
from discord.ext import commands
import discord

class OnlineBehaviour(commands.Cog):
    def __init__(self, client: McDisClient):
        self.client = client
        
        self.config_online = \
            {  'Thumbnail'      : 'https://i.postimg.cc/XqQx5rT5/logo.png',
                'Embed Colour'  : 0x2f3136,
                'ChannelID'     : 930324106455416883}

    @commands.Cog.listener()
    async def on_message                (self, message: discord.Message):
        description = ''
        
        if message.channel.id != self.config_online['ChannelID']:
            return
        
        elif self.client.is_command(message.content, 'online'):
            for server in self.client.servers:
                server : AeServer

                description += f'`[{server.name}]`: '
                description += ', '.join(server.online_players)
                description += '\n\n'

            await message.channel.send(embed = self.online_list_embed('Usuarios conectados:', description))
        
        elif self.client.is_command(message.content, 'bots'):
            for server in self.client.servers:
                server: AeServer

                description += f'`[{server.name}]`: '
                description += ', '.join(server.bots)
                description += '\n\n'
        
            await message.channel.send(embed = self.online_list_embed('Bots:', description))

    def       online_list_embed         (self, title: str, description: str):
        embed = discord.Embed(
                title = title,
                colour = self.config_online['Embed Colour'],
                description = description)
        
        embed.set_thumbnail(url = self.config_online['Thumbnail'])
        
        return embed
    
async def setup(client: McDisClient):
    await client.add_cog(OnlineBehaviour(client))
