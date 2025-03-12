from mcdis_rcon.utils import isAdmin
from discord.ext import commands
import discord

class edit_message(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

        @client.tree.context_menu(
                name = 'Edit Message')
        
        async def edit_message(interaction: discord.Interaction, message: discord.Message):
            if not isAdmin(interaction.user):
                await interaction.response.send_message('✖ No tienes permisos.', ephemeral = True, delete_after = 1)
                return
            elif not message.author.id == self.client.user.id:
                await interaction.response.send_message('✖ Este mensaje no le pertenece al bot.', ephemeral = True, delete_after = 2)
                return
                        
            default = message.content

            class edit_message_modal(discord.ui.Modal, title = 'Editar mensaje'):
                new_message = discord.ui.TextInput(label = 'Mensaje', style = discord.TextStyle.paragraph, default = default)
                
                async def on_submit(self, interaction: discord.Interaction):    
                    await message.edit(content = self.new_message)
                    await interaction.response.send_message('✔', ephemeral = True, delete_after = 1)   
            await interaction.response.send_modal(edit_message_modal())

async def setup(client: commands.Bot):
    await client.add_cog(edit_message(client))