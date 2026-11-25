from __future__ import annotations

from pathlib import Path

import aiomcrcon  # type: ignore[import-untyped]

from .properties import read_properties, write_properties


class RconError(Exception):
    """Raised when a Minecraft RCON connection, authentication, or command fails."""


async def rcon_execute(
    host: str,
    port: int,
    password: str,
    command: str,
    *,
    timeout: float = 5.0,
) -> str:
    """Connect to a Minecraft RCON server via ``aiomcrcon``, execute ``command``, and return output."""
    try:
        async with aiomcrcon.Client(host, port, password) as client:
            response, _msg_type = await client.send_cmd(command, timeout=timeout)
            return str(response)
    except (aiomcrcon.RCONConnectionError, aiomcrcon.IncorrectPasswordError, aiomcrcon.ClientNotConnectedError) as exc:
        raise RconError(str(exc)) from exc


def ensure_rcon_properties(
    properties_path: Path,
    *,
    password: str,
    port_offset: int,
) -> int | None:
    """Ensure ``enable-rcon=true``, ``rcon.port=server-port+3500``, and ``rcon.password`` exist.

    Returns ``rcon_port`` if ``properties_path`` exists and defines ``server-port``, otherwise ``None``.
    """
    if not properties_path.is_file() or not password:
        return None

    props = read_properties(properties_path)
    try:
        server_port = int(props['server-port'])
    except (KeyError, ValueError):
        return None

    rcon_port = server_port + port_offset
    desired = {
        'enable-rcon': 'true',
        'rcon.port': str(rcon_port),
        'rcon.password': password,
    }
    if any(props.get(key) != value for key, value in desired.items()):
        props.update(desired)
        write_properties(properties_path, props)

    return rcon_port
