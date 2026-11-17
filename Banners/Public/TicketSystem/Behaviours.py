from __future__ import annotations

import discord
from discord.ext import commands
from dismanager.classes import DisManagerClient

from ..Form.LogInteraction import update_log as update_form_log
from .LogInteraction import is_ticket, ticket_info_update


class TicketSystemBehaviour(commands.Cog):
    """Sync ticket and form logs when a ticket channel is manually deleted."""

    def __init__(self, client: DisManagerClient) -> None:
        self.client = client

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel) -> None:
        if not is_ticket(channel.id):
            return

        ticket_info_update(channel.id, {'state': 'closed'})
        await update_form_log(self.client)


async def setup(client: DisManagerClient) -> None:
    """Register the TicketSystemBehaviour cog on ``client``."""
    await client.add_cog(TicketSystemBehaviour(client))
