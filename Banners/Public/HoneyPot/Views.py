from __future__ import annotations

from typing import cast

import discord
from Classes.config import get_ae_config
from dismanager.classes import DisManagerClient
from Utils.discord_helpers import get_or_create_thread

from .Modules import get_honeypot_ban_count, resolve_honeypot_channel

_BEE_EMOJI = '🐝'
_THUMBNAIL_URL = (
    'https://images-ext-1.discordapp.net/external/CFFcxTz-dvRCg5dWUuAAzAugpjj1KAvnkVB89Z69ZXQ/'
    'https/raw.githubusercontent.com/microsoft/fluentui-emoji/refs/heads/main/assets/'
    'Honey%2520pot/3D/honey_pot_3d.png?format=webp&quality=lossless&width=320&height=320'
)


class _EnLanguageButton(discord.ui.Button['HoneyPotView']):
    def __init__(self) -> None:
        super().__init__(
            label='En',
            style=discord.ButtonStyle.secondary,
            custom_id='honeypot:lang_en',
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        client = cast(DisManagerClient, interaction.client)
        channel = resolve_honeypot_channel(client)
        hp_cfg = get_ae_config(client).honeypot
        log_thread = await get_or_create_thread('HoneyPot Log', channel, public=True)
        await interaction.response.send_message(
            view=HoneyPotEnView(
                accent_color=hp_cfg.accent_color,
                log_thread_id=log_thread.id,
            ),
            ephemeral=True,
        )


class _BeeCounterButton(discord.ui.Button['HoneyPotView']):
    def __init__(self, ban_count: int) -> None:
        super().__init__(
            label=f' {ban_count}',
            emoji=_BEE_EMOJI,
            style=discord.ButtonStyle.secondary,
            custom_id='honeypot:bee_counter',
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()


class HoneyPotEnView(discord.ui.LayoutView):
    """Ephemeral Components v2 English warning view."""

    def __init__(self, *, accent_color: int, log_thread_id: int) -> None:
        super().__init__(timeout=60)
        container: discord.ui.Container[HoneyPotEnView] = discord.ui.Container(
            discord.ui.Section(
                discord.ui.TextDisplay(
                    '## ⚠️ DO NOT SEND MESSAGES\n'
                    'If you send a message here, you will be banned. '
                    'This channel is used to detect spam bots or compromised accounts.\n\n'
                    f'<#{log_thread_id}>'
                ),
                accessory=discord.ui.Thumbnail(_THUMBNAIL_URL),
            ),
            accent_colour=accent_color,
        )
        self.add_item(container)


class HoneyPotView(discord.ui.LayoutView):
    """Persistent Components v2 HoneyPot warning banner and ban counter."""

    def __init__(self, *, accent_color: int, log_thread_id: int, ban_count: int) -> None:
        super().__init__(timeout=None)
        container: discord.ui.Container[HoneyPotView] = discord.ui.Container(
            discord.ui.Section(
                discord.ui.TextDisplay(
                    '## ⚠️ NO ENVIAR MENSAJES\n'
                    'Si envías un mensaje aquí, serás baneado. '
                    'Este canal se usa para detectar spam de bots o cuentas hackeadas.\n\n'
                    f'<#{log_thread_id}>'
                ),
                accessory=discord.ui.Thumbnail(_THUMBNAIL_URL),
            ),
            discord.ui.Separator(),
            discord.ui.ActionRow(
                _EnLanguageButton(),
                _BeeCounterButton(ban_count),
            ),
            accent_colour=accent_color,
        )
        self.add_item(container)


async def build_honeypot_view(client: DisManagerClient) -> HoneyPotView:
    """Build the Components v2 ``HoneyPotView`` from ``client`` configuration and stats."""
    hp_cfg = get_ae_config(client).honeypot
    channel = resolve_honeypot_channel(client)
    log_thread = await get_or_create_thread('HoneyPot Log', channel, public=True)
    return HoneyPotView(
        accent_color=hp_cfg.accent_color,
        log_thread_id=log_thread.id,
        ban_count=get_honeypot_ban_count(),
    )
