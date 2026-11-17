from __future__ import annotations

import asyncio
import traceback

import aiohttp
import discord
from Classes.config import get_ae_config
from dismanager.classes import DisManagerClient

from .Embeds import banner_es_embed
from .Views import BannerEsViews


async def discord_creator(client: DisManagerClient, *, loop: bool = False) -> None:
    """Create or refresh the persistent DiscordInfo banner message."""
    ae_cfg = get_ae_config(client)
    discord_cfg = ae_cfg.discord_info
    channel_id = discord_cfg.channel_id
    channel = client.get_channel(channel_id)
    if not isinstance(channel, discord.TextChannel):
        return

    while True:
        try:
            messages = [msg async for msg in channel.history(limit=None, oldest_first=True)]
            view = BannerEsViews(ae_cfg.server_emoji)
            embed = banner_es_embed(
                discord_cfg.invite,
                foundation_date=discord_cfg.foundation_date,
                thumbnail=ae_cfg.thumbnail,
            )

            if not messages:
                sent = await channel.send(embed=embed, view=view)
                await channel.send(discord_cfg.invite)
                client.add_view(view, message_id=sent.id)
            elif (
                len(messages) == 2
                and client.user is not None
                and all(msg.author.id == client.user.id for msg in messages)
            ):
                await messages[0].edit(embed=embed, view=view)
                await messages[1].edit(content=discord_cfg.invite)
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
