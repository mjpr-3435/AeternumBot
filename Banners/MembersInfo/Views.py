from __future__ import annotations

from typing import cast

import discord
from dismanager.classes import DisManagerClient

from Classes import get_ae_config
from Utils.discord_helpers import is_admin

from .Embeds import apoyo_embed, twitch_embed
from .Whitelist import WhitelistListView, whitelist_embed


class MembersInfoView(discord.ui.View):
    """Persistent action buttons for the MembersInfo banner."""

    def __init__(self) -> None:
        super().__init__(timeout=None)

    @discord.ui.button(
        label='Whitelist',
        style=discord.ButtonStyle.gray,
        custom_id='members_info:whitelist',
    )
    async def whitelist_button(
        self,
        interaction: discord.Interaction,
        _button: discord.ui.Button[MembersInfoView],
    ) -> None:
        client = cast(DisManagerClient, interaction.client)
        role_id = get_ae_config(client).tickets.interviewer_role_id
        has_interviewer = isinstance(interaction.user, discord.Member) and any(
            role.id == role_id for role in interaction.user.roles
        )
        user_is_admin = isinstance(interaction.user, discord.Member) and is_admin(interaction.user)

        await interaction.response.send_message(
            embed=whitelist_embed(client),
            view=WhitelistListView(is_admin_request=user_is_admin or has_interviewer),
            ephemeral=True,
        )

    @discord.ui.button(
        label='Server Jobs',
        style=discord.ButtonStyle.gray,
        custom_id='members_info:server_jobs',
    )
    async def apoyo_button(
        self,
        interaction: discord.Interaction,
        _button: discord.ui.Button[MembersInfoView],
    ) -> None:
        client = cast(DisManagerClient, interaction.client)
        await interaction.response.send_message(
            embeds=apoyo_embed(get_ae_config(client).thumbnail),
            ephemeral=True,
        )

    @discord.ui.button(
        label='Twitch',
        style=discord.ButtonStyle.gray,
        custom_id='members_info:twitch',
    )
    async def twitch_button(
        self,
        interaction: discord.Interaction,
        _button: discord.ui.Button[MembersInfoView],
    ) -> None:
        client = cast(DisManagerClient, interaction.client)
        embed, files = twitch_embed(get_ae_config(client).members_info.twitch_stream_key)
        await interaction.response.send_message(embed=embed, files=files, ephemeral=True)
