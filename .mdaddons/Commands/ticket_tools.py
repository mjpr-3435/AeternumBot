from mcdis_rcon.utils import isAdmin
from discord.ext import commands
from discord.app_commands import choices, Choice

import discord

class TicketToolsCommand(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.interviewer_id = 914530780523401267

    @discord.app_commands.command(
        name            = 'ticket',
        description     = 'Dar roles a los miembros de prueba'
    )        
    @choices(action = [Choice(name = i, value = i) for i in ['Accept', 'Reject', 'Voting', 'Incomplete']])

    async def ticket_tools_command(self,
        interaction: discord.Interaction, 
        action: Choice[str],
        ping: discord.Member):

        if not isAdmin(interaction.user) and not self.interviewer_id in [role.id for role in interaction.user.roles]:
            await interaction.response.send_message('✖ No tienes permisos.', ephemeral = True, delete_after = 1)
            return
        
        await interaction.response.defer(thinking = True, ephemeral = True)

        EMOJIS = {
            'Accept': '✅',
            'Reject': '❌',
            'Voting': '❔',
            'Incomplete': '❗'
        }

        def rename_channel_with_emoji(current_name, new_emoji):
            if current_name and current_name[0] in EMOJIS.values():
                return new_emoji + current_name[1:]
            return new_emoji + current_name

        if action.value == 'Accept':
            msg = (
                "\n\nEs un placer informarte que tu formulario ha sido aceptado. Nos gustaría coordinar una entrevista contigo para discutir en detalle tu experiencia, habilidades y expectativas con respecto a la posición."
                "\n\nPor favor, indícanos los días y horas que te resulten más convenientes para la entrevista. Estamos dispuestos a ajustarnos a tu horario tanto como sea posible."
                "\n\nEsperamos con interés tener la oportunidad de conversar contigo y conocerte mejor. ¡Gracias por tu dedicación y entusiasmo por formar parte de nuestro servidor!"
            )

            new_name = rename_channel_with_emoji(interaction.channel.name, EMOJIS['Accept'])
            await interaction.channel.edit(name=new_name)
            await interaction.channel.send(f"{msg}\n\n{ping.mention}")

        elif action.value == 'Reject':
            msg = (
                "¡Hola!"
                "\n\nGracias por tu interés en unirte a nuestro servidor. Lamentablemente, hemos decidido no aceptar tu solicitud en este momento."
                "\n\nSi deseas volver a postular, puedes volver a hacerlo dentro de 3 meses."
                "\n\n¡Te deseamos lo mejor en tu camino hacia la excelencia en Minecraft Técnico!"
            )
            new_name = rename_channel_with_emoji(interaction.channel.name, EMOJIS['Reject'])
            await interaction.channel.edit(name=new_name)
            await interaction.channel.send(f"{msg}\n\n{ping.mention}")
        
        elif action.value == 'Voting':
            new_name = rename_channel_with_emoji(interaction.channel.name, EMOJIS['Voting'])
            await interaction.channel.edit(name=new_name)

        elif action.value == 'Incomplete':
            new_name = rename_channel_with_emoji(interaction.channel.name, EMOJIS['Incomplete'])
            await interaction.channel.edit(name=new_name)

        await interaction.followup.send('✔')


async def setup(client: commands.Bot):
    await client.add_cog(TicketToolsCommand(client))
