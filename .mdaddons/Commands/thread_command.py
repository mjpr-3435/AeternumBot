from mcdis_rcon.utils import isAdmin, thread

from discord.app_commands import describe
from discord.ext import commands
import discord

class ThreadCommand(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        
        @client.tree.command(
            name = 'thread', 
            description = 'Crea un hilo en el canal actual'
        )
        @describe(title='Título del hilo', public='Si el hilo será público o no')
        async def thread_command(interaction: discord.Interaction, title: str, public: bool = True):
            if not isAdmin(interaction.user):
                await interaction.response.send_message(
                    "✖ No tienes permisos.", ephemeral=True, delete_after=1
                )
                return
            
            await thread(name = title, channel = interaction.channel, public = public)

            await interaction.response.send_message('✔', ephemeral=True)

async def setup(client: commands.Bot):
    await client.add_cog(ThreadCommand(client))
