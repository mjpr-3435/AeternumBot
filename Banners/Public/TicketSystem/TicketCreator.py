from __future__ import annotations

from typing import cast

import discord
from dismanager.classes import DisManagerClient

from Classes import get_ae_config

from .LogInteraction import (
    new_log,
    new_ticket_number,
    ticket_id_from_user,
    ticket_info_update,
)
from .TicketBanner import ticket_banner_embed
from .TicketViews import TicketBannerView


async def ticket_creation(
    interaction: discord.Interaction,
    lang: str = 'es',
) -> tuple[discord.TextChannel, bool]:
    """Return an existing open ticket for ``interaction.user`` or create a new one."""
    client = cast(DisManagerClient, interaction.client)
    existing_id = ticket_id_from_user(interaction.user)
    if existing_id:
        existing = client.get_channel(existing_id)
        if isinstance(existing, discord.TextChannel):
            return existing, False

    guild = interaction.guild
    if guild is None:
        raise ValueError('Ticket creation requires a guild interaction.')

    ae_config = get_ae_config(client)
    category = next(
        (cat for cat in guild.categories if cat.id == ae_config.discord_info.tickets_category_id),
        None,
    )
    interviewer = guild.get_role(ae_config.tickets.interviewer_role_id)
    ticket_number = new_ticket_number()

    ticket_permissions = discord.PermissionOverwrite(
        read_messages=True,
        send_messages=True,
        create_public_threads=True,
        send_messages_in_threads=True,
    )
    overwrites: dict[discord.Role | discord.Member | discord.Object, discord.PermissionOverwrite] = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
    }
    if isinstance(interaction.user, discord.Member):
        overwrites[interaction.user] = ticket_permissions
    if interviewer is not None:
        overwrites[interviewer] = ticket_permissions

    created_ticket = await guild.create_text_channel(
        f'ticket-{interaction.user.display_name}',
        category=category,
        overwrites=overwrites,
    )
    ticket_banner = await created_ticket.send(
        content=interaction.user.mention,
        embed=ticket_banner_embed(interaction.user, ticket_number, lang=lang),
        view=TicketBannerView(lang=lang),
    )

    new_log(ticket_banner, interaction)
    ticket_info_update(created_ticket.id, {'lang': lang})
    return created_ticket, True
