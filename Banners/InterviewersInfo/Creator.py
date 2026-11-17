from __future__ import annotations

from pathlib import Path

import discord
from Classes.config import AeternumConfig, get_ae_config
from dismanager.classes import DisManagerClient
from Utils.discord_helpers import get_or_create_thread

from .Views import InterviewersInfoView

_EMBED_COLOUR = 0x2F3136
_BANNER_PATH = Path(__file__).resolve().parent / 'Banner.png'


async def interviewers_creator(client: DisManagerClient) -> None:
    """Create or update the persistent InterviewersInfo banner message."""
    ae_cfg = get_ae_config(client)
    channel_id = ae_cfg.interviewers_info.channel_id
    channel = client.get_channel(channel_id)
    if not isinstance(channel, discord.TextChannel):
        return

    messages = [msg async for msg in channel.history(limit=None, oldest_first=True)]
    banner = await _interviewers_embed(channel, ae_cfg=ae_cfg)
    view = InterviewersInfoView(ae_cfg.thumbnail)

    if not messages:
        sent = await channel.send(
            embed=banner,
            file=discord.File(_BANNER_PATH),
            view=view,
        )
        client.add_view(view, message_id=sent.id)
    elif client.user is not None and messages[0].author.id == client.user.id:
        await messages[0].edit(embed=banner, view=view)
        client.add_view(view, message_id=messages[0].id)


async def interviewers_extras(client: DisManagerClient) -> None:
    """Background hook reserved for InterviewersInfo extras."""
    _ = client


async def _interviewers_embed(channel: discord.TextChannel, *, ae_cfg: AeternumConfig) -> discord.Embed:
    resources_thread = await get_or_create_thread(
        'Recursos de Entrevistadores',
        channel,
        public=True,
    )
    polls_thread = await get_or_create_thread('Encuestas', channel, public=True)
    forms_ch = (
        f'<#{ae_cfg.discord_info.forms_channel_id}>'
        if ae_cfg.discord_info.forms_channel_id > 0
        else '`Canal no definido`'
    )
    members_ch = (
        f'<#{ae_cfg.members_info.channel_id}>'
        if ae_cfg.members_info.channel_id > 0
        else '`Canal no definido`'
    )

    return (
        discord.Embed(
            title='Entrevistadores',
            colour=_EMBED_COLOUR,
            description=(
                'El rol de entrevistador se asigna a miembros de confianza que hayan '
                'sido activos recientemente en el servidor. Este rol les permite participar '
                'en la selección de nuevos miembros, así como en las discusiones de '
                'organización y proyectos.'
            ),
        )
        .add_field(name='', inline=True, value=f'<#{resources_thread.id}>')
        .add_field(name='', inline=True, value=f'<#{polls_thread.id}>')
        .add_field(
            name='> Qué hace un entrevistador',
            inline=False,
            value=(
                f'- Puede ver los formularios en {forms_ch} y votar.\n'
                '- Puede ver y escribir en los tickets.\n'
                '- Coordina entrevistas cuando haga falta.\n'
                '- Marca el estado del ticket con `/ticket`.\n'
                f'- Añade o remueve gente de la whitelist desde {members_ch}.'
            ),
        )
        .set_thumbnail(url=ae_cfg.thumbnail)
    )
