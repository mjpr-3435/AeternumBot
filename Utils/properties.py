from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path


def read_properties(path: str | Path) -> dict[str, str]:
    """Read a ``.properties`` file into a ``{key: value}`` dictionary."""
    file_path = Path(path)
    if not file_path.is_file():
        return {}

    result: dict[str, str] = {}
    for line in file_path.read_text(encoding='utf-8').splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith('#') or '=' not in stripped:
            continue
        key, value = stripped.split('=', 1)
        result[key.strip()] = value.strip()
    return result


def write_properties(path: str | Path, properties: Mapping[str, str]) -> None:
    """Write ``properties`` to ``path``, preserving existing comments and key order."""
    file_path = Path(path)
    existing_lines = file_path.read_text(encoding='utf-8').splitlines() if file_path.is_file() else []

    updated_lines: list[str] = []
    seen: set[str] = set()

    for line in existing_lines:
        stripped = line.strip()
        if stripped and not stripped.startswith('#') and '=' in stripped:
            key, _ = stripped.split('=', 1)
            key = key.strip()
            if key in properties:
                seen.add(key)
                updated_lines.append(f'{key}={properties[key]}')
                continue
        updated_lines.append(line)

    for key, value in properties.items():
        if key not in seen:
            updated_lines.append(f'{key}={value}')

    file_path.write_text('\n'.join(updated_lines) + ('\n' if updated_lines else ''), encoding='utf-8')
