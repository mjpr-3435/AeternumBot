from .Creator import members_creator
from .Modules import *
from .TaskLog import *

class TaskCommand(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        
        @client.tree.command(
            name = 'task', 
            description = 'Administra los hilos de tareas',
            extras = {'rank' : 3})

        @describe(name          = 'Nombre del hilo de tareas')
        @describe(action        = 'Acción que quieres hacer con el hilo')
        @choices (action        = [Choice(name = i, value = i) for i in ['Create', 'Close']])

        async def task_command(interaction: discord.Interaction, action: Choice[str], name : str):
            if not isAdmin(interaction.user):
                await interaction.response.send_message('✖ No tienes permisos.', ephemeral = True, delete_after = 1)
                return

            await interaction.response.defer(ephemeral = True)

            dummy = [thread for thread in self.client.get_channel(config['Channel ID']).threads if thread.name.lower() == name.lower() and is_task(thread)]

            if action.value == 'Create':
                if len(dummy) != 0:
                    await interaction.followup.send('✖ Ya existe una tarea con ese nombre.')
                    return
                
                message = await self.client.get_channel(config['Channel ID']).send(f'Hilo público creado.')
                thread = await message.create_thread(name = name.strip())
                await message.delete()

                new_log(thread)
                await members_creator(interaction.client, loop = False)
                
                await interaction.followup.send('✔')

            elif action.value == 'Close':
                if len(dummy) == 0:
                    await interaction.followup.send('✖ No existe una tarea con ese nombre.')
                    return
                
                thread = dummy[0]
                
                await thread.delete()
                del_log(thread)
                await members_creator(interaction.client, loop = False)
                await interaction.followup.send('✔')

async def setup(client: commands.Bot):
    await client.add_cog(TaskCommand(client))
