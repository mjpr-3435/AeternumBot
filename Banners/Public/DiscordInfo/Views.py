from __future__ import annotations

from typing import cast

import discord
from Classes.config import get_ae_config
from dismanager.classes import DisManagerClient

from ..TicketSystem.TicketCreator import ticket_creation
from .Embeds import (
    apply_en_embed,
    apply_es_embed,
    banner_en_embed,
    hardware_info_embed,
    rules_en_embed,
    rules_es_embed,
)


class BannerEnViews(discord.ui.View):
    """Ephemeral English DiscordInfo view."""

    def __init__(self, server_emoji: str) -> None:
        super().__init__(timeout=900)
        for child in self.children:
            if isinstance(child, discord.ui.Button) and child.label != 'Tickets':
                child.emoji = server_emoji

    @discord.ui.button(
        label='Server Info',
        style=discord.ButtonStyle.gray,
    )
    async def server_info_button(
        self,
        interaction: discord.Interaction,
        _button: discord.ui.Button[BannerEnViews],
    ) -> None:
        client = cast(DisManagerClient, interaction.client)
        await interaction.response.send_message(
            embed=hardware_info_embed(get_ae_config(client).discord_info),
            ephemeral=True,
        )

    @discord.ui.button(
        label='Apply',
        style=discord.ButtonStyle.gray,
    )
    async def apply_button(
        self,
        interaction: discord.Interaction,
        _button: discord.ui.Button[BannerEnViews],
    ) -> None:
        await interaction.response.send_message(embeds=apply_en_embed(), ephemeral=True)

    @discord.ui.button(
        label='Rules',
        style=discord.ButtonStyle.gray,
    )
    async def rules_button(
        self,
        interaction: discord.Interaction,
        _button: discord.ui.Button[BannerEnViews],
    ) -> None:
        await interaction.response.send_message(embeds=rules_en_embed(), ephemeral=True)

    @discord.ui.button(label='Tickets', emoji='📩', style=discord.ButtonStyle.blurple)
    async def form_button(
        self,
        interaction: discord.Interaction,
        _button: discord.ui.Button[BannerEnViews],
    ) -> None:
        await interaction.response.defer(thinking=True, ephemeral=True)
        ticket, created_ticket = await ticket_creation(interaction, lang='en')
        msg = (
            f'Ticket created <#{ticket.id}>.'
            if created_ticket
            else f'✖ You already have an open ticket. <#{ticket.id}>'
        )
        response = await interaction.followup.send(msg, wait=True)
        await response.delete(delay=60)


class BannerEsViews(discord.ui.View):
    """Persistent Spanish DiscordInfo banner controls."""

    def __init__(self, server_emoji: str) -> None:
        super().__init__(timeout=None)
        self._server_emoji = server_emoji
        for child in self.children:
            if isinstance(child, discord.ui.Button) and child.custom_id != 'discord_info:tickets':
                child.emoji = server_emoji

    @discord.ui.button(
        label='En',
        style=discord.ButtonStyle.gray,
        custom_id='discord_info:en',
    )
    async def en_button(
        self,
        interaction: discord.Interaction,
        _button: discord.ui.Button[BannerEsViews],
    ) -> None:
        client = cast(DisManagerClient, interaction.client)
        ae_cfg = get_ae_config(client)
        await interaction.response.send_message(
            embed=banner_en_embed(
                ae_cfg.discord_info.invite,
                foundation_date=ae_cfg.discord_info.foundation_date,
                thumbnail=ae_cfg.thumbnail,
                version=ae_cfg.minecraft_version,
                links=ae_cfg.discord_info.links,
            ),
            ephemeral=True,
            view=BannerEnViews(self._server_emoji),
        )

    @discord.ui.button(
        label='Server Info',
        style=discord.ButtonStyle.gray,
        custom_id='discord_info:server_info',
    )
    async def server_info_button(
        self,
        interaction: discord.Interaction,
        _button: discord.ui.Button[BannerEsViews],
    ) -> None:
        client = cast(DisManagerClient, interaction.client)
        await interaction.response.send_message(
            embed=hardware_info_embed(get_ae_config(client).discord_info),
            ephemeral=True,
        )

    @discord.ui.button(
        label='Apply',
        style=discord.ButtonStyle.gray,
        custom_id='discord_info:apply',
    )
    async def apply_button(
        self,
        interaction: discord.Interaction,
        _button: discord.ui.Button[BannerEsViews],
    ) -> None:
        await interaction.response.send_message(embeds=apply_es_embed(), ephemeral=True)

    @discord.ui.button(
        label='Rules',
        style=discord.ButtonStyle.gray,
        custom_id='discord_info:rules',
    )
    async def rules_button(
        self,
        interaction: discord.Interaction,
        _button: discord.ui.Button[BannerEsViews],
    ) -> None:
        await interaction.response.send_message(embeds=rules_es_embed(), ephemeral=True)

    @discord.ui.button(
        label='Tickets',
        emoji='📩',
        style=discord.ButtonStyle.blurple,
        custom_id='discord_info:tickets',
    )
    async def form_button(
        self,
        interaction: discord.Interaction,
        _button: discord.ui.Button[BannerEsViews],
    ) -> None:
        await interaction.response.defer(thinking=True, ephemeral=True)
        ticket, created_ticket = await ticket_creation(interaction, lang='es')
        if not created_ticket:
            response = await interaction.followup.send(
                f'✖ Ya tienes un ticket abierto. <#{ticket.id}>',
                wait=True,
            )
            await response.delete(delay=5)
        else:
            response = await interaction.followup.send(f'Ticket creado <#{ticket.id}>.', wait=True)
            await response.delete(delay=60)
