import asyncio
import aiohttp
import discord
import json
import os
import traceback

from datetime import datetime, timezone

from mcdis_rcon.classes import McDisClient
from mcdis_rcon.utils import thread

config = {
    "Channel ID": 1490889830970691715,
    "Accent Color": 0xF2B632,
    "Bee Emoji": "🐝",
    "Thumbnail": "https://i.postimg.cc/XqQx5rT5/logo.png",
    "Log Thread Name": "HoneyPot Log",
    "Button Cooldown": 5,
    "Ban Reason": "HoneyPot triggered: message sent in restricted security channel.",
}

stats_path = os.path.join(os.path.dirname(__file__), "HoneyPotStats.json")


def resolve_honeypot_channel(client: McDisClient):
    channel = client.get_channel(config["Channel ID"])

    if channel is None:
        raise ValueError(f'HoneyPot channel {config["Channel ID"]} no existe o no está en caché.')

    if isinstance(channel, discord.CategoryChannel):
        raise TypeError(
            f'HoneyPot channel {config["Channel ID"]} apunta a una categoría ({channel.name}). '
            'Usa el ID de un canal de texto.'
        )

    if not hasattr(channel, "history") or not hasattr(channel, "send"):
        raise TypeError(
            f'HoneyPot channel {config["Channel ID"]} no es un canal compatible para banners.'
        )

    return channel


def default_honeypot_stats() -> dict:
    return {
        "banned": [],
        "failed": [],
    }


def load_honeypot_stats() -> dict:
    if not os.path.exists(stats_path):
        stats = default_honeypot_stats()
        save_honeypot_stats(stats)
        return stats

    with open(stats_path, "r", encoding="utf-8") as file:
        stats = json.load(file)

    stats.setdefault("banned", [])
    stats.setdefault("failed", [])
    return stats


def save_honeypot_stats(stats: dict):
    with open(stats_path, "w", encoding="utf-8") as file:
        json.dump(stats, file, indent=2, ensure_ascii=False)


def get_honeypot_ban_count() -> int:
    return len(load_honeypot_stats()["banned"])


def build_honeypot_record(message: discord.Message, *, error: str | None = None) -> dict:
    return {
        "user_id": int(message.author.id),
        "username": str(message.author),
        "message_id": int(message.id),
        "channel_id": int(message.channel.id),
        "content": message.content,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "error": error,
    }


def register_honeypot_ban(message: discord.Message) -> bool:
    stats = load_honeypot_stats()
    record = build_honeypot_record(message)

    if any(entry["user_id"] == record["user_id"] for entry in stats["banned"]):
        return False

    stats["banned"].append(record)
    save_honeypot_stats(stats)
    return True


def register_honeypot_failed_ban(message: discord.Message, error: str):
    stats = load_honeypot_stats()
    stats["failed"].append(build_honeypot_record(message, error=error))
    save_honeypot_stats(stats)


async def find_honeypot_banner_message(client: McDisClient):
    channel = resolve_honeypot_channel(client)
    messages = [msg async for msg in channel.history(limit=25, oldest_first=True)]

    for message in messages:
        if message.author.id == client.user.id and message.embeds:
            return message

    return None
