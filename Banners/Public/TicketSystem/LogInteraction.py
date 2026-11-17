from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import discord
from dismanager.classes import DisManagerClient

_TICKETS_LOG_PATH = Path(__file__).resolve().parent / 'tickets.json'


def _load_state() -> dict[str, Any]:
    if not _TICKETS_LOG_PATH.is_file():
        return {'next_number': 1, 'tickets': {}}
    raw = json.loads(_TICKETS_LOG_PATH.read_text(encoding='utf-8'))
    if not isinstance(raw, dict):
        return {'next_number': 1, 'tickets': {}}
    raw.setdefault('next_number', 1)
    raw.setdefault('tickets', {})
    return raw


def _save_state(state: dict[str, Any]) -> None:
    _TICKETS_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = _TICKETS_LOG_PATH.with_suffix('.tmp')
    tmp.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding='utf-8')
    tmp.replace(_TICKETS_LOG_PATH)


def is_ticket(channel_id: int) -> bool:
    """Return whether ``channel_id`` is a registered ticket channel."""
    return str(channel_id) in _load_state()['tickets']


def new_log(ticket_banner: discord.Message, interaction: discord.Interaction) -> None:
    """Register a newly created ticket channel in ``tickets.json``."""
    state = _load_state()
    ticket_number = int(state['next_number'])
    state['next_number'] = ticket_number + 1
    state['tickets'][str(ticket_banner.channel.id)] = {
        'state': 'active',
        'ticket_channel_id': ticket_banner.channel.id,
        'ticket_banner_id': ticket_banner.id,
        'owner_id': interaction.user.id,
        'ticket_number': ticket_number,
        'lang': 'es',
    }
    _save_state(state)


def new_ticket_number() -> int:
    """Return the next ticket sequence number."""
    return int(_load_state()['next_number'])


def ticket_id_from_user(user: discord.abc.User) -> int:
    """Return the active ticket channel ID owned by ``user``, or ``0`` if none."""
    for entry in _load_state()['tickets'].values():
        if entry.get('state') == 'active' and entry.get('owner_id') == user.id:
            return int(entry['ticket_channel_id'])
    return 0


def ticket_info_request(ticket_channel_id: int, request: list[str]) -> Any:
    """Fetch one or more stored fields for ``ticket_channel_id``."""
    entry = _load_state()['tickets'].get(str(ticket_channel_id))
    if entry is None:
        return None if len(request) == 1 else tuple(None for _ in request)
    values = [entry.get(key) for key in request]
    return values[0] if len(request) == 1 else tuple(values)


def ticket_info_update(ticket_channel_id: int, new_values: dict[str, Any]) -> None:
    """Update stored fields for ``ticket_channel_id``."""
    state = _load_state()
    entry = state['tickets'].get(str(ticket_channel_id))
    if entry is None:
        return
    entry.update(new_values)
    _save_state(state)


def get_active_tickets() -> list[dict[str, Any]]:
    """Return all currently active ticket records."""
    return [
        entry
        for entry in _load_state()['tickets'].values()
        if isinstance(entry, dict) and entry.get('state') == 'active'
    ]


async def update_log(client: DisManagerClient) -> None:
    """Mark any active ticket whose Discord channel no longer exists as ``closed``."""
    state = _load_state()
    changed = False
    for entry in state['tickets'].values():
        if entry.get('state') != 'active':
            continue
        if client.get_channel(int(entry['ticket_channel_id'])) is None:
            entry['state'] = 'closed'
            changed = True
    if changed:
        _save_state(state)
