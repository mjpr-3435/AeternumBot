from __future__ import annotations

import contextlib
import json
from pathlib import Path

import discord
from dismanager.classes import DisManagerClient

_TASKS_PATH = Path(__file__).resolve().parent / 'tasks.json'


def _load_thread_ids() -> list[int]:
    if not _TASKS_PATH.is_file():
        return []
    raw = json.loads(_TASKS_PATH.read_text(encoding='utf-8'))
    if not isinstance(raw, list):
        return []
    return [int(item) for item in raw]


def _save_thread_ids(thread_ids: list[int]) -> None:
    tmp = _TASKS_PATH.with_suffix('.tmp')
    tmp.write_text(json.dumps(thread_ids, indent=2), encoding='utf-8')
    tmp.replace(_TASKS_PATH)


def is_task(thread: discord.Thread) -> bool:
    """Return whether ``thread`` is a registered project task thread."""
    return thread.id in _load_thread_ids()


def del_log(thread: discord.Thread) -> None:
    """Unregister ``thread`` from ``tasks.json``."""
    thread_ids = [tid for tid in _load_thread_ids() if tid != thread.id]
    _save_thread_ids(thread_ids)


def new_log(thread: discord.Thread) -> None:
    """Register ``thread`` in ``tasks.json`` if not already present."""
    thread_ids = _load_thread_ids()
    if thread.id not in thread_ids:
        thread_ids.append(thread.id)
        _save_thread_ids(thread_ids)


def show_tasks(client: DisManagerClient) -> str:
    """Return bullet-joined mentions of all active registered task threads."""
    valid = [tid for tid in _load_thread_ids() if client.get_channel(tid) is not None]
    return ' • '.join(f'<#{tid}>' for tid in valid)


async def update_log(client: DisManagerClient) -> None:
    """Unarchive existing task threads and prune deleted ones from ``tasks.json``."""
    kept: list[int] = []
    for thread_id in _load_thread_ids():
        try:
            channel = await client.fetch_channel(thread_id)
            if isinstance(channel, discord.Thread):
                await channel.edit(archived=False)
                kept.append(thread_id)
        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
            with contextlib.suppress(Exception):
                pass
    _save_thread_ids(kept)
