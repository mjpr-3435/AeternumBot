from __future__ import annotations

import contextlib
import json
from pathlib import Path
from typing import Any

import discord
from dismanager.classes import DisManagerClient

_FORMS_LOG_PATH = Path(__file__).resolve().parent / 'forms.json'


def _load_forms() -> dict[str, dict[str, Any]]:
    if not _FORMS_LOG_PATH.is_file():
        return {}
    raw = json.loads(_FORMS_LOG_PATH.read_text(encoding='utf-8'))
    return raw if isinstance(raw, dict) else {}


def _save_forms(data: dict[str, dict[str, Any]]) -> None:
    _FORMS_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = _FORMS_LOG_PATH.with_suffix('.tmp')
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    tmp.replace(_FORMS_LOG_PATH)


def form_info_request(form_id: int, request: list[str]) -> Any:
    """Fetch one or more stored fields for ``form_id``."""
    entry = _load_forms().get(str(form_id))
    if entry is None:
        return None if len(request) == 1 else tuple(None for _ in request)
    values = [entry.get(key) for key in request]
    return values[0] if len(request) == 1 else tuple(values)


def form_info_update(form_id: int, new_values: dict[str, Any]) -> None:
    """Update stored fields for ``form_id``."""
    data = _load_forms()
    entry = data.get(str(form_id))
    if entry is None:
        return
    entry.update(new_values)
    _save_forms(data)


def new_log(message: discord.Message, user_id: int, lang: str = 'es') -> None:
    """Register a newly posted application form message."""
    data = _load_forms()
    data[str(message.id)] = {
        'form_id': message.id,
        'channel_id': message.channel.id,
        'message_id': message.id,
        'log_message_id': 0,
        'owner_id': user_id,
        'lang': lang,
        'completed': [],
    }
    _save_forms(data)


def get_completed_sections(form_id: int) -> set[str]:
    """Return the set of completed form sections for ``form_id``."""
    entry = _load_forms().get(str(form_id))
    if entry is None:
        return set()
    raw = entry.get('completed', [])
    completed = {str(item) for item in raw if isinstance(item, str)} if isinstance(raw, list) else set()
    if int(entry.get('log_message_id', 0) or 0) > 0:
        completed.add('personal')
    return completed


def mark_section_completed(
    form_id: int,
    section: str,
    *,
    log_message_id: int | None = None,
) -> tuple[int, str, set[str]]:
    """Mark ``section`` completed for ``form_id`` and return ``(owner_id, lang, completed)``."""
    data = _load_forms()
    entry = data.get(str(form_id))
    if entry is None:
        return 0, 'es', {section}

    if log_message_id is not None:
        entry['log_message_id'] = log_message_id

    raw = entry.get('completed', [])
    completed = [str(item) for item in raw if isinstance(item, str)] if isinstance(raw, list) else []
    if int(entry.get('log_message_id', 0) or 0) > 0 and 'personal' not in completed:
        completed.append('personal')
    if section not in completed:
        completed.append(section)
    entry['completed'] = completed
    _save_forms(data)
    return int(entry.get('owner_id', 0)), str(entry.get('lang', 'es')), set(completed)


async def reactive_views(client: DisManagerClient) -> None:
    """Reattach interactive button views with persisted completion state to active form messages."""
    from .FormViews import FormBannerView

    for entry in _load_forms().values():
        channel = client.get_channel(int(entry['channel_id']))
        if not isinstance(channel, discord.abc.Messageable):
            continue
        msg_id = int(entry['message_id'])
        completed = get_completed_sections(msg_id)
        view = FormBannerView(
            int(entry['owner_id']),
            lang=str(entry.get('lang', 'es')),
            completed=completed,
        )
        client.add_view(view, message_id=msg_id)
        with contextlib.suppress(Exception):
            form_msg = await channel.fetch_message(msg_id)
            await form_msg.edit(view=view)


async def update_log(client: DisManagerClient) -> None:
    """Remove form entries whose ticket channel no longer exists."""
    data = _load_forms()
    cleaned = {
        key: entry
        for key, entry in data.items()
        if client.get_channel(int(entry['channel_id'])) is not None
    }
    if len(cleaned) != len(data):
        _save_forms(cleaned)
