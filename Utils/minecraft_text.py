from __future__ import annotations

import json
from typing import Any


def truncate(text: str, max_length: int) -> str:
    """Truncate ``text`` to ``max_length`` characters with an ellipsis if needed."""
    return text if len(text) < max_length else f'{text[: max_length - 3]}...'


def extras(components: list[str], *, text: str = '', color: str = 'gray') -> str:
    """Build a Minecraft 1.21.5+ text component wrapping serialized ``extra`` components."""
    joined = ', '.join(components)
    return f'{{"text": {json.dumps(text)}, "color": {json.dumps(color)}, "extra": [{joined}]}}'


def hover(text: str, *, color: str = 'gray', hover: str) -> str:
    """Build a Minecraft 1.21.5+ text component with a ``show_text`` hover_event."""
    payload: dict[str, Any] = {
        'text': text,
        'color': color,
        'hover_event': {'action': 'show_text', 'value': hover},
    }
    return json.dumps(payload)


def hover_and_suggest(text: str, *, color: str = 'gray', suggest: str, hover: str) -> str:
    """Build a Minecraft 1.21.5+ text component with ``suggest_command`` and ``show_text``."""
    payload: dict[str, Any] = {
        'text': text,
        'color': color,
        'click_event': {'action': 'suggest_command', 'command': suggest},
        'hover_event': {'action': 'show_text', 'value': hover},
    }
    return json.dumps(payload)


def hover_and_run(text: str, *, color: str = 'gray', command: str, hover: str) -> str:
    """Build a Minecraft 1.21.5+ text component with ``run_command`` and ``show_text``."""
    payload: dict[str, Any] = {
        'text': text,
        'color': color,
        'click_event': {'action': 'run_command', 'command': command},
        'hover_event': {'action': 'show_text', 'value': hover},
    }
    return json.dumps(payload)
