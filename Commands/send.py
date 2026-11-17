from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands
from dismanager.classes import DisManagerClient

from Utils.discord_helpers import is_admin


class _SendMessageModal(discord.ui.Modal, title='Enviar mensaje'):
    message: discord.ui.TextInput[_SendMessageModal] = discord.ui.TextInput(
        label='Mensaje',
        style=discord.TextStyle.paragraph,
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        if isinstance(interaction.channel, discord.abc.Messageable):
            await interaction.channel.send(self.message.value)
        await interaction.response.send_message('✔', ephemeral=True, delete_after=1)


class SendCommand(commands.Cog):
    """Admin-only slash command to send a message as the bot."""

    def __init__(self, client: DisManagerClient) -> None:
        self.client = client

    @app_commands.command(
        name='send',
        description='Haz que el bot envíe un mensaje',
    )
    async def send_command(self, interaction: discord.Interaction) -> None:
        if not isinstance(interaction.user, discord.Member) or not is_admin(interaction.user):
            await interaction.response.send_message(
                '✖ No tienes permisos.',
                ephemeral=True,
                delete_after=1,
            )
            return

        await interaction.response.send_modal(_SendMessageModal())


async def setup(client: DisManagerClient) -> None:
    """Register the SendCommand cog on ``client``."""
    await client.add_cog(SendCommand(client))
