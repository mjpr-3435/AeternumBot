from .Modules import *
from mcdis_rcon.utils import isAdmin,thread
from .Creator import discord_creator

class MemberListCommand(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        
        @client.tree.command(
            name = 'MembersList', 
            description = 'Administra los miembros del servidor.',
            extras = {'rank' : 3})

        @describe(name          = 'Nickname del miembro')
        @describe(action        = 'Acción que quieres hacer')
        @describe(emoji_id      = 'ID del emoji del miembro (opcional)')
        @choices (action        = [Choice(name = i, value = i) for i in ['Add', 'Remove']])

        async def task_command(interaction: discord.Interaction, name : str, action: Choice[str], emoji_id: int = None):
            if not isAdmin(interaction.user):
                await interaction.response.send_message('✖ No tienes permisos.', ephemeral = True, delete_after = 1)
                return

            await interaction.response.defer(thinking=True, ephemeral = True)

            if action.value == 'Add':
                if not emoji_id:
                    await interaction.followup.send('✖ Debes proporcionar un ID de emoji.', ephemeral = True)
                    return
                
                channel = interaction.client.get_channel(config['Channel ID'])
                member_thread = await thread(name, channel, public = True)

                df = pd.read_csv(members_list_path)

                nueva_fila = {
                    "name": name.strip(),
                    "emojji_id": emoji_id,
                    "thread_id": member_thread.id
                }

                df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)
                df.to_csv(members_list_path, index=False)


                await discord_creator(interaction.client)
                await interaction.followup.send('✔')

            elif action.value == 'Remove':
                df = pd.read_csv(members_list_path)
                df = df.loc[df['name'] != name.strip()]
                df.to_csv(members_list_path, index=False)

                await discord_creator(interaction.client)
                await interaction.followup.send('✔')

async def setup(client: commands.Bot):
    await client.add_cog(MemberListCommand(client))
