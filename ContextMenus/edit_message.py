from __future__ import annotations

import discord
from discord.ext import commands
from dismanager.classes import DisManagerClient
from Utils.discord_helpers import is_admin


class _EditMessageModal(discord.ui.Modal, title='Editar mensaje'):
    new_message: discord.ui.TextInput[_EditMessageModal]

    def __init__(self, target_message: discord.Message) -> None:
        super().__init__()
        self._target_message = target_message
        self.new_message = discord.ui.TextInput(
            style=discord.TextStyle.paragraph,
            default=target_message.content,
        )
        self.add_item(discord.ui.Label(text='Mensaje', component=self.new_message))

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await self._target_message.edit(content=self.new_message.value)
        await interaction.response.send_message('✔', ephemeral=True, delete_after=1)


class EditMessageContextMenu(commands.Cog):
    """Admin-only context menu to edit messages sent by the bot."""

    def __init__(self, client: DisManagerClient) -> None:
        self.client = client

        @client.tree.context_menu(name='Edit Message')
        async def edit_message(
            interaction: discord.Interaction,
            message: discord.Message,
        ) -> None:
            if not isinstance(interaction.user, discord.Member) or not is_admin(interaction.user):
                await interaction.response.send_message(
                    '✖ No tienes permisos.',
                    ephemeral=True,
                    delete_after=1,
                )
                return

            if self.client.user is None or message.author.id != self.client.user.id:
                await interaction.response.send_message(
                    '✖ Este mensaje no le pertenece al bot.',
                    ephemeral=True,
                    delete_after=2,
                )
                return

            await interaction.response.send_modal(_EditMessageModal(message))


async def setup(client: DisManagerClient) -> None:
    """Register the EditMessageContextMenu cog on ``client``."""
    await client.add_cog(EditMessageContextMenu(client))
