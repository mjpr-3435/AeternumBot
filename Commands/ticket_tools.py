from __future__ import annotations

import discord
from discord import app_commands
from discord.app_commands import Choice, choices
from discord.ext import commands
from dismanager.classes import DisManagerClient

from Classes import get_ae_config
from Utils.discord_helpers import is_admin

_EMOJIS: dict[str, str] = {
    'Accept': '✅',
    'Reject': '❌',
    'Voting': '❔',
    'Incomplete': '❗',
}


def _rename_channel_with_emoji(current_name: str, new_emoji: str) -> str:
    if current_name and current_name[0] in _EMOJIS.values():
        return new_emoji + current_name[1:]
    return new_emoji + current_name


class TicketToolsCommand(commands.Cog):
    """Slash command for interviewers and admins to manage application tickets."""

    def __init__(self, client: DisManagerClient) -> None:
        self.client = client

    def _interviewer_role_id(self) -> int:
        return get_ae_config(self.client).tickets.interviewer_role_id

    @app_commands.command(
        name='ticket',
        description='Dar roles a los miembros de prueba',
    )
    @choices(
        action=[
            Choice(name=name, value=name)
            for name in ('Accept', 'Reject', 'Voting', 'Incomplete')
        ]
    )
    async def ticket_tools_command(
        self,
        interaction: discord.Interaction,
        action: Choice[str],
        ping: discord.Member,
    ) -> None:
        if not isinstance(interaction.user, discord.Member):
            await interaction.response.send_message(
                '✖ No tienes permisos.',
                ephemeral=True,
                delete_after=1,
            )
            return

        interviewer_role_id = self._interviewer_role_id()
        has_interviewer_role = any(
            role.id == interviewer_role_id for role in interaction.user.roles
        )
        if not is_admin(interaction.user) and not has_interviewer_role:
            await interaction.response.send_message(
                '✖ No tienes permisos.',
                ephemeral=True,
                delete_after=1,
            )
            return

        if not isinstance(interaction.channel, discord.TextChannel):
            await interaction.response.send_message(
                '✖ Este comando solo puede usarse en canales de texto.',
                ephemeral=True,
                delete_after=2,
            )
            return

        await interaction.response.defer(thinking=True, ephemeral=True)

        new_name = _rename_channel_with_emoji(
            interaction.channel.name,
            _EMOJIS[action.value],
        )
        await interaction.channel.edit(name=new_name)

        if action.value == 'Accept':
            msg = (
                '\n\nEs un placer informarte que tu formulario ha sido aceptado. '
                'Nos gustaría coordinar una entrevista contigo para discutir en detalle '
                'tu experiencia, habilidades y expectativas con respecto a la posición.'
                '\n\nPor favor, indícanos los días y horas que te resulten más '
                'convenientes para la entrevista. Estamos dispuestos a ajustarnos a tu '
                'horario tanto como sea posible.'
                '\n\nEsperamos con interés tener la oportunidad de conversar contigo y '
                'conocerte mejor. ¡Gracias por tu dedicación y entusiasmo por formar '
                'parte de nuestro servidor!'
            )
            await interaction.channel.send(f'{msg}\n\n{ping.mention}')
        elif action.value == 'Reject':
            msg = (
                '¡Hola!'
                '\n\nGracias por tu interés en unirte a nuestro servidor. '
                'Lamentablemente, hemos decidido no aceptar tu solicitud en este momento.'
                '\n\nSi deseas volver a postular, puedes volver a hacerlo dentro de 3 meses.'
                '\n\n¡Te deseamos lo mejor en tu camino hacia la excelencia en Minecraft Técnico!'
            )
            await interaction.channel.send(f'{msg}\n\n{ping.mention}')

        await interaction.followup.send('✔')


async def setup(client: DisManagerClient) -> None:
    """Register the TicketToolsCommand cog on ``client``."""
    await client.add_cog(TicketToolsCommand(client))
