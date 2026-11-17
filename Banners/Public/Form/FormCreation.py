from __future__ import annotations

import discord
from dismanager.classes import DisManagerClient

from .FormBanner import form_banner_embed
from .FormViews import FormBannerView
from .LogInteraction import new_log


async def form_creation(
    client: DisManagerClient,
    channel: discord.abc.Messageable,
    user_id: int,
    lang: str = 'es',
) -> None:
    """Post an application form embed and register it."""
    form = await channel.send(
        embed=form_banner_embed(client, lang=lang),
        view=FormBannerView(user_id, lang=lang),
    )
    new_log(form, user_id, lang=lang)
