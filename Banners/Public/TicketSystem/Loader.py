from __future__ import annotations

import contextlib

import discord
from dismanager.classes import DisManagerClient

from .LogInteraction import get_active_tickets, update_log
from .TicketViews import TicketBannerView


async def load(client: DisManagerClient) -> None:
    """Sync ticket logs and reattach persistent views to open tickets."""
    await update_log(client)
    client.add_view(TicketBannerView(lang='es'))
    client.add_view(TicketBannerView(lang='en'))

    for row in get_active_tickets():
        channel = client.get_channel(int(row['ticket_channel_id']))
        if not isinstance(channel, discord.abc.Messageable):
            continue
        with contextlib.suppress(Exception):
            message = await channel.fetch_message(int(row['ticket_banner_id']))
            lang = str(row.get('lang', 'es'))
            await message.edit(view=TicketBannerView(lang=lang))
