from __future__ import annotations

import csv
import json
import shutil
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import TypedDict

from Classes import get_ae_servers
from dismanager.classes import DisManagerClient
from Utils.minecraft_api import mc_uuid

_BASE_DIR = Path(__file__).resolve().parent
WHITELIST_LOG_PATH = _BASE_DIR / 'WhitelistLog.csv'
WHITELIST_JSON_PATH = _BASE_DIR / 'Whitelist.json'


class WhitelistEntry(TypedDict):
    """Single row stored in ``WhitelistLog.csv``."""

    index: int
    nickname: str
    user_id: int
    date: str


def load_whitelist_rows() -> list[WhitelistEntry]:
    """Read and index-sort all rows from ``WhitelistLog.csv``."""
    if not WHITELIST_LOG_PATH.is_file():
        return []
    rows: list[WhitelistEntry] = []
    with WHITELIST_LOG_PATH.open('r', encoding='utf-8', newline='') as file:
        for row in csv.DictReader(file):
            rows.append({
                'index': int(row['index']),
                'nickname': row['nickname'],
                'user_id': int(row['user_id']),
                'date': row['date'],
            })
    rows.sort(key=lambda item: item['index'])
    return rows


def save_whitelist_rows(rows: list[WhitelistEntry]) -> None:
    """Write ``rows`` atomically to ``WhitelistLog.csv`` with renumbered indices."""
    tmp = WHITELIST_LOG_PATH.with_suffix('.tmp')
    with tmp.open('w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=('index', 'nickname', 'user_id', 'date'))
        writer.writeheader()
        for idx, row in enumerate(rows):
            writer.writerow({
                'index': idx,
                'nickname': row['nickname'],
                'user_id': row['user_id'],
                'date': row['date'],
            })
    tmp.replace(WHITELIST_LOG_PATH)


def filter_whitelist_rows(*, inactives_only: bool = False) -> list[WhitelistEntry]:
    """Return all whitelist rows, or only those inactive for >90 days."""
    rows = load_whitelist_rows()
    if not inactives_only:
        return rows

    cutoff = date.today() - timedelta(days=90)
    inactives: list[WhitelistEntry] = []
    for row in rows:
        parsed = parse_iso_date(row['date'])
        if parsed is None or parsed < cutoff:
            inactives.append(row)
    return inactives


def parse_iso_date(value: str) -> date | None:
    """Parse ``YYYY-MM-DD`` or return ``None`` when unregistered/invalid."""
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError:
        return None


def _load_mc_whitelist() -> list[dict[str, str]]:
    if not WHITELIST_JSON_PATH.is_file():
        return []
    raw = json.loads(WHITELIST_JSON_PATH.read_text(encoding='utf-8'))
    return raw if isinstance(raw, list) else []


def _save_mc_whitelist(entries: list[dict[str, str]]) -> None:
    tmp = WHITELIST_JSON_PATH.with_suffix('.tmp')
    tmp.write_text(json.dumps(entries, indent=2), encoding='utf-8')
    tmp.replace(WHITELIST_JSON_PATH)


def add_to_mc_whitelist(nickname: str) -> None:
    """Add online and offline UUID entries for ``nickname`` to ``Whitelist.json``."""
    uuid_offline = mc_uuid(player=nickname, online=False)
    uuid_online = mc_uuid(player=nickname, online=True)
    whitelist = _load_mc_whitelist()

    changed = False
    for uuid_val in (uuid_offline, uuid_online):
        if uuid_val is None:
            continue
        if not any(entry.get('uuid') == uuid_val for entry in whitelist):
            whitelist.append({'uuid': uuid_val, 'name': nickname})
            changed = True

    if changed:
        _save_mc_whitelist(whitelist)


def remove_from_mc_whitelist(nickname: str) -> None:
    """Remove all entries matching ``nickname`` (case-insensitive) from ``Whitelist.json``."""
    whitelist = _load_mc_whitelist()
    target = nickname.casefold()
    updated = [entry for entry in whitelist if str(entry.get('name', '')).casefold() != target]
    if len(updated) != len(whitelist):
        _save_mc_whitelist(updated)


def purge_inactive_whitelist_entries(
    excluded_nicknames: list[str] | None = None,
) -> tuple[list[str], list[str]]:
    """Remove inactive whitelist entries except ``excluded_nicknames``."""
    inactive_rows = filter_whitelist_rows(inactives_only=True)
    if not inactive_rows:
        return [], []

    excluded_lc = {nick.casefold() for nick in (excluded_nicknames or [])}
    excluded_applied = [
        row['nickname'] for row in inactive_rows if row['nickname'].casefold() in excluded_lc
    ]
    to_remove = [
        row['nickname'] for row in inactive_rows if row['nickname'].casefold() not in excluded_lc
    ]
    if not to_remove:
        return [], excluded_applied

    remove_lc = {nick.casefold() for nick in to_remove}
    kept_rows = [
        row for row in load_whitelist_rows() if row['nickname'].casefold() not in remove_lc
    ]
    save_whitelist_rows(kept_rows)

    whitelist = _load_mc_whitelist()
    new_whitelist = [
        entry for entry in whitelist if str(entry.get('name', '')).casefold() not in remove_lc
    ]
    if len(new_whitelist) != len(whitelist):
        _save_mc_whitelist(new_whitelist)

    return to_remove, excluded_applied


def update_player_date(player: str) -> None:
    """Update ``WhitelistLog.csv`` last-seen ``date`` for ``player`` to today."""
    rows = load_whitelist_rows()
    today = date.today().isoformat()
    changed = False
    for row in rows:
        if row['nickname'] == player and row['date'] != today:
            row['date'] = today
            changed = True
    if changed:
        save_whitelist_rows(rows)


def update_whitelist_on_servers(client: DisManagerClient) -> None:
    """Sync ``Whitelist.json`` to every configured ``AeServer`` and run ``whitelist reload``."""
    if not WHITELIST_JSON_PATH.is_file():
        return
    for server in get_ae_servers(client).values():
        dest = server.path / 'server' / 'whitelist.json'
        if not dest.parent.is_dir():
            continue
        shutil.copy2(WHITELIST_JSON_PATH, dest)
        if server.is_running():
            server.execute('whitelist reload')
