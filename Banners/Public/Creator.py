from __future__ import annotations

import asyncio

from dismanager.classes import DisManagerClient

from .DiscordInfo.Creator import discord_creator
from .Form.Loader import load as load_forms
from .HoneyPot.Creator import honey_pot_creator
from .Showcase.ShowcaseTools import load_showcase_controls
from .TicketSystem.Loader import load as load_tickets


async def public_creator(client: DisManagerClient, *, loop: bool = False) -> None:
    """Create or refresh public-facing banners."""
    await asyncio.gather(
        discord_creator(client, loop=loop),
        honey_pot_creator(client),
    )


async def public_extras(client: DisManagerClient) -> None:
    """Initialize Public cogs, TicketSystem, Form, and Showcase controls."""
    extensions = (
        'Banners.Public.TicketSystem.Behaviours',
        'Banners.Public.Showcase.ShowcaseCommand',
    )
    for extension in extensions:
        if extension in client.extensions:
            await client.unload_extension(extension)
        await client.load_extension(extension)

    await load_tickets(client)
    await load_forms(client)
    await load_showcase_controls(client)
