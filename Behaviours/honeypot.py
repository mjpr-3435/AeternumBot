from __future__ import annotations

import discord
from Banners.Public.HoneyPot.Modules import (
    find_honeypot_banner_message,
    increment_honeypot_ban_count,
    resolve_honeypot_channel,
)
from Banners.Public.HoneyPot.Views import build_honeypot_view
from Classes import get_ae_config
from discord.ext import commands
from dismanager.classes import DisManagerClient
from Utils.discord_helpers import get_or_create_thread


class HoneyPotBehaviour(commands.Cog):
    """Listen to the HoneyPot security channel, ban offenders, and log incidents."""

    def __init__(self, client: DisManagerClient) -> None:
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot or message.guild is None:
            return
        ae_config = get_ae_config(self.client)
        if message.channel.id != ae_config.honeypot.channel_id:
            return
        if not isinstance(message.author, discord.Member):
            return

        await self.delete_honeypot_message(message)

        try:
            await message.author.ban(
                reason=ae_config.honeypot.ban_reason,
                delete_message_seconds=ae_config.honeypot.delete_message_seconds,
            )
        except discord.HTTPException:
            return

        increment_honeypot_ban_count()
        await self.send_log_entry(message)
        await self.refresh_honeypot_counter()

    async def delete_honeypot_message(self, message: discord.Message) -> None:
        try:
            await message.delete()
        except discord.HTTPException:
            pass

    async def send_log_entry(self, message: discord.Message) -> None:
        channel = resolve_honeypot_channel(self.client)
        if not isinstance(channel, discord.TextChannel):
            return
        ae_config = get_ae_config(self.client)
        log_thread = await get_or_create_thread(
            ae_config.honeypot.log_thread_name,
            channel,
            public=True,
        )
        await log_thread.send(embed=self.build_log_embed(message))

    def build_log_embed(self, message: discord.Message) -> discord.Embed:
        ae_config = get_ae_config(self.client)
        content = message.content.strip() or '[sin texto]'
        if len(content) > 1000:
            content = content[:997] + '...'

        embed = discord.Embed(
            title='HoneyPot Log',
            colour=ae_config.honeypot.accent_color,
            description=(
                f'Usuario baneado: {message.author.mention}\n'
                f'ID: `{message.author.id}`\n'
                f'Canal: <#{ae_config.honeypot.channel_id}>'
            ),
        )
        embed.add_field(name='Mensaje', value=content, inline=False)
        embed.set_thumbnail(url=message.author.display_avatar.url)
        return embed

    async def refresh_honeypot_counter(self) -> None:
        banner_message = await find_honeypot_banner_message(self.client)
        if banner_message is None:
            return
        view = await build_honeypot_view(self.client)
        await banner_message.edit(view=view, embeds=[])


async def setup(client: DisManagerClient) -> None:
    """Register the HoneyPotBehaviour cog on ``client``."""
    await client.add_cog(HoneyPotBehaviour(client))
