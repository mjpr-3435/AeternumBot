from __future__ import annotations

import contextlib
import hashlib
import json
import urllib.request
import uuid

_NIL_UUID = '00000000-0000-0000-0000-000000000000'


def mc_uuid(player: str, *, online: bool = True) -> str:
    """Return the Mojang online UUID or offline v3 UUID for ``player``."""
    if not online:
        hashed = bytearray(hashlib.md5(f'OfflinePlayer:{player}'.encode()).digest())
        hashed[6] = (hashed[6] & 0x0F) | 0x30
        hashed[8] = (hashed[8] & 0x3F) | 0x80
        return str(uuid.UUID(bytes=bytes(hashed)))

    with contextlib.suppress(OSError, json.JSONDecodeError, KeyError, ValueError):
        req = urllib.request.Request(
            f'https://api.mojang.com/users/profiles/minecraft/{player}',
            headers={'User-Agent': 'AeternumBot'},
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode('utf-8'))
                return str(uuid.UUID(data['id']))
    return _NIL_UUID


def online_uuid_to_name(player_uuid: str) -> str:
    """Resolve an online Minecraft ``player_uuid`` to its current username."""
    with contextlib.suppress(OSError, json.JSONDecodeError, ValueError):
        req = urllib.request.Request(
            f'https://sessionserver.mojang.com/session/minecraft/profile/{player_uuid}',
            headers={'User-Agent': 'AeternumBot'},
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode('utf-8'))
                return str(data.get('name', 'unknown'))
    return 'unknown'
