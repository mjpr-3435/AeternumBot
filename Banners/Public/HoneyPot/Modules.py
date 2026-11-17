from __future__ import annotations

import json
from pathlib import Path

import discord
from Classes.config import get_ae_config
from dismanager.classes import DisManagerClient

_STATS_PATH = Path(__file__).resolve().parent / 'HoneyPotStats.json'


def resolve_honeypot_channel(client: DisManagerClient) -> discord.TextChannel:
    """Resolve and validate the configured HoneyPot text channel."""
    channel_id = get_ae_config(client).honeypot.channel_id
    channel = client.get_channel(channel_id)
    if channel is None:
        raise ValueError(f'HoneyPot channel {channel_id} no existe o no está en caché.')
    if not isinstance(channel, discord.TextChannel):
        raise TypeError(f'HoneyPot channel {channel_id} debe ser un canal de texto.')
    return channel


def get_honeypot_ban_count() -> int:
    """Return the persisted HoneyPot ban count."""
    if not _STATS_PATH.is_file():
        _save_count(0)
        return 0

    raw = json.loads(_STATS_PATH.read_text(encoding='utf-8'))
    if not isinstance(raw, dict):
        return 0
    count = raw.get('count', 0)
    return count if isinstance(count, int) else 0


def increment_honeypot_ban_count() -> int:
    """Increment and persist the HoneyPot ban counter, returning the new count."""
    new_count = get_honeypot_ban_count() + 1
    _save_count(new_count)
    return new_count


def _save_count(count: int) -> None:
    tmp = _STATS_PATH.with_suffix('.tmp')
    tmp.write_text(json.dumps({'count': count}, indent=2), encoding='utf-8')
    tmp.replace(_STATS_PATH)


async def find_honeypot_banner_message(client: DisManagerClient) -> discord.Message | None:
    """Find the existing HoneyPot banner message sent by the bot, if present."""
    channel = resolve_honeypot_channel(client)
    if client.user is None:
        return None

    async for message in channel.history(limit=25, oldest_first=True):
        if message.author.id == client.user.id and (message.components or message.embeds):
            return message
    return None
