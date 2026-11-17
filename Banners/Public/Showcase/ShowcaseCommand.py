from __future__ import annotations

import contextlib

import discord
from Classes.config import get_ae_config
from discord import app_commands
from discord.ext import commands
from dismanager.classes import DisManagerClient
from Utils.discord_helpers import is_admin

from .ShowcaseTools import ShowcasePostMenuView, default_post_text, thread_name


class ShowcaseCommand(commands.Cog):
    """Admin-only slash command to create managed posts in the Showcase channel."""

    def __init__(self, client: DisManagerClient) -> None:
        self.client = client

    @app_commands.command(
        name='showcase_post',
        description='Crea un post nuevo en Showcase',
    )
    @app_commands.describe(
        title='Titulo del post',
        image='Imagen principal del post',
        text='Texto del mensaje principal',
    )
    async def showcase_post(
        self,
        interaction: discord.Interaction,
        title: str,
        image: discord.Attachment,
        text: str | None = None,
    ) -> None:
        if not isinstance(interaction.user, discord.Member) or not is_admin(interaction.user):
            await interaction.response.send_message('No tienes permisos.', ephemeral=True, delete_after=2)
            return

        if image.content_type is not None and not image.content_type.startswith('image/'):
            await interaction.response.send_message('El archivo debe ser una imagen.', ephemeral=True)
            return

        ae_cfg = get_ae_config(self.client)
        channel = self.client.get_channel(ae_cfg.discord_info.showcase_id)
        if not isinstance(channel, discord.TextChannel):
            await interaction.response.send_message('No encontre el canal de Showcase.', ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        post_message = await channel.send(
            content=(text or '').strip() or default_post_text(title),
            file=await image.to_file(),
            view=ShowcasePostMenuView(),
        )
        await post_message.create_thread(name=thread_name(title))
        if ae_cfg.server_emoji.strip():
            with contextlib.suppress(discord.HTTPException):
                await post_message.add_reaction(ae_cfg.server_emoji)

        await interaction.followup.send(f'Post creado: {post_message.jump_url}', ephemeral=True)


async def setup(client: DisManagerClient) -> None:
    """Register the ShowcaseCommand cog on ``client``."""
    await client.add_cog(ShowcaseCommand(client))
