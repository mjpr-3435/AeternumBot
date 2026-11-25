from __future__ import annotations

import asyncio
import traceback

import aiohttp
import discord
from Classes.config import get_ae_config
from dismanager.classes import DisManagerClient

from .Modules import find_honeypot_banner_message, resolve_honeypot_channel
from .Views import build_honeypot_view


async def honey_pot_creator(client: DisManagerClient) -> None:
    """Create or update the persistent Components v2 HoneyPot banner."""
    if get_ae_config(client).honeypot.channel_id <= 0:
        return
    try:
        channel = resolve_honeypot_channel(client)
        banner_message = await find_honeypot_banner_message(client)
        view = await build_honeypot_view(client)

        if banner_message is None:
            sent = await channel.send(view=view)
            client.add_view(view, message_id=sent.id)
        else:
            await banner_message.edit(view=view, embeds=[])
            client.add_view(view, message_id=banner_message.id)
    except asyncio.CancelledError:
        return
    except (aiohttp.ClientError, discord.HTTPException):
        await asyncio.sleep(1)
        await honey_pot_creator(client)
    except Exception:
        print(f'Error:\n{traceback.format_exc()}')


async def honey_pot_extras(client: DisManagerClient) -> None:
    """Background hook reserved for HoneyPot extras."""
    _ = client
