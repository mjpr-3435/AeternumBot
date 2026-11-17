from __future__ import annotations

import asyncio
import traceback
from datetime import datetime
from pathlib import Path

import aiohttp
import discord
from dismanager.classes import DisManagerClient

from Classes import get_ae_config
from Utils.discord_helpers import get_or_create_thread

from .Tasks.TaskLog import show_tasks, update_log
from .Views import MembersInfoView
from .Whitelist import update_whitelist_on_servers

_BANNER_PATH = Path(__file__).resolve().parent / 'Banner.png'


async def members_creator(client: DisManagerClient, *, loop: bool = True) -> None:
    """Create or refresh the persistent MembersInfo banner message."""
    channel_id = get_ae_config(client).members_info.channel_id
    channel = client.get_channel(channel_id)
    if not isinstance(channel, discord.TextChannel):
        return

    update_whitelist_on_servers(client)

    while True:
        try:
            messages = [msg async for msg in channel.history(limit=None, oldest_first=True)]
            banner = await _banner_embed(client, channel)
            view = MembersInfoView()

            if not messages:
                sent = await channel.send(
                    embed=banner,
                    file=discord.File(_BANNER_PATH),
                    view=view,
                )
                client.add_view(view, message_id=sent.id)
            elif (
                len(messages) == 1
                and client.user is not None
                and messages[0].author.id == client.user.id
            ):
                await messages[0].edit(embed=banner, view=view)
                client.add_view(view, message_id=messages[0].id)
            else:
                await channel.purge(limit=100)
                continue

            if not loop:
                break
        except asyncio.CancelledError:
            return
        except (aiohttp.ClientError, discord.HTTPException):
            reloaded = client.get_channel(channel_id)
            if isinstance(reloaded, discord.TextChannel):
                channel = reloaded
            await asyncio.sleep(1)
            continue
        except Exception:
            print(f'Error:\n{traceback.format_exc()}')
        else:
            await asyncio.sleep(24 * 60 * 60)


async def members_extras(client: DisManagerClient) -> None:
    """Initialize task thread logs and MembersInfo cogs."""
    await update_log(client)

    extensions = (
        'Banners.MembersInfo.Tasks.TaskCommand',
        'Banners.MembersInfo.Tasks.TaskBehaviour',
    )
    for extension in extensions:
        if extension in client.extensions:
            await client.unload_extension(extension)
        await client.load_extension(extension)

    await client.tree.sync()


async def _banner_embed(client: DisManagerClient, channel: discord.TextChannel) -> discord.Embed:
    ae_cfg = get_ae_config(client)
    mi_cfg = ae_cfg.members_info
    foundation = ae_cfg.discord_info.foundation_date
    days_total = (datetime.now().date() - datetime.strptime(foundation, '%Y-%m-%d').date()).days
    years, days = int(days_total // 365.25), int(days_total % 365.25)

    if years == 0:
        active_days = f'Tiempo activo: {days} días'
    elif days == 0:
        active_days = f'Tiempo activo: {years} años'
    else:
        active_days = f'Tiempo activo: {years} años {days} días'

    announcements = await get_or_create_thread('Announcements', channel, public=True)
    whitelist_log = await get_or_create_thread('Whitelist Log', channel, public=True)
    server_log = await get_or_create_thread('Server Log', channel, public=True)

    pad = ' ' * 41
    return (
        discord.Embed(colour=0x2F3136)
        .add_field(
            name='> Información del servidor',
            inline=False,
            value=(
                '||```prolog\n'
                f"{('Ip:' + pad)[:-len(mi_cfg.ip_server)]}{mi_cfg.ip_server}\n"
                f"{('Ip Plugins:' + pad)[:-len(mi_cfg.ip_plugins)]}{mi_cfg.ip_plugins}\n"
                f"{('Ip Dummy:' + pad)[:-len(mi_cfg.ip_dummy)]}{mi_cfg.ip_dummy}\n"
                f"{('Seed:' + pad)[:-len(mi_cfg.seed)]}{mi_cfg.seed}"
                '```||\n'
            ),
        )
        .add_field(name='', inline=True, value=f'<#{announcements.id}>')
        .add_field(name='', inline=True, value=f'<#{whitelist_log.id}>')
        .add_field(name='', inline=True, value=f'<#{server_log.id}>')
        .add_field(name='', inline=True, value=f"Fundación: {foundation.replace('-', '/')}")
        .add_field(name='', inline=True, value=active_days)
        .add_field(
            name='',
            inline=False,
            value=f'`    💸 Donaciones: {mi_cfg.paypal_link}    `',
        )
        .add_field(
            name='> Reglas para miembros',
            inline=False,
            value=(
                '- No filtrar mensajes fuera del servidor.\n'
                '- No se tolerará ningún tipo de toxicidad.\n'
                '- Quien grifee el servidor será baneado permanente.\n'
                '- Si se llegara a romper una granja, AVISA. Nadie te va a decir nada.\n'
                '- No está permitida la duplicación de ítems.\n'
                ' Excepciones: bloques con gravedad, elitrós y esponjas.'
            ),
        )
        .add_field(
            name='> Tareas de Proyectos:',
            inline=False,
            value=show_tasks(client) or '—',
        )
        .set_thumbnail(url=ae_cfg.thumbnail)
    )
