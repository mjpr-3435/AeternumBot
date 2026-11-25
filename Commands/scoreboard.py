from __future__ import annotations

import json
import time
from typing import Any

import discord
from Classes.AeServer import AeServer
from Classes.config import get_ae_config
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands
from dismanager.classes import DisManagerClient
from Utils.rcon import RconError, rcon_execute

PAGE_SIZE = 15
_LIST_CACHE_TTL_S = 20.0
_LIST_CACHE: dict[str, tuple[float, list[dict[str, Any]]]] = {}

_STAT_CATEGORIES = (
    'mined',
    'used',
    'crafted',
    'broken',
    'picked_up',
    'dropped',
    'killed',
    'killed_by',
    'custom',
)


def _get_servers(client: DisManagerClient) -> dict[str, AeServer]:
    servers = getattr(client, 'ae_servers', None)
    return servers if isinstance(servers, dict) else {}


def _resolve_server(client: DisManagerClient) -> tuple[str, AeServer] | None:
    servers = _get_servers(client)
    if not servers:
        return None
    for k, srv in servers.items():
        if srv.rcon_port is not None and srv.is_running():
            return k, srv
    first_key = next(iter(servers))
    return first_key, servers[first_key]


def _get_logo_url(client: DisManagerClient) -> str | None:
    try:
        thumb = (get_ae_config(client).thumbnail or '').strip()
        if thumb:
            return thumb
    except Exception:
        pass
    if client.user is not None:
        return client.user.display_avatar.url
    return None


async def _rcon_json(server: AeServer, command: str) -> dict[str, Any]:
    if server.rcon_port is None:
        return {'ok': False, 'error': 'RCON no está disponible en este servidor.'}
    try:
        raw = await rcon_execute('127.0.0.1', server.rcon_port, server.rcon_password, command)
    except (OSError, TimeoutError, RconError) as exc:
        return {'ok': False, 'error': f'Error RCON: {exc}'}
    raw = (raw or '').strip()
    if not raw:
        return {'ok': False, 'error': 'Respuesta vacía de RCON.'}
    try:
        data = json.loads(raw)
        return data if isinstance(data, dict) else {'ok': False, 'error': 'Respuesta JSON inválida.'}
    except json.JSONDecodeError:
        return {'ok': False, 'error': raw[:300]}


async def _fetch_objectives_cached(server_key: str, server: AeServer) -> list[dict[str, Any]]:
    now = time.monotonic()
    cached = _LIST_CACHE.get(server_key)
    if cached is not None and (now - cached[0]) < _LIST_CACHE_TTL_S:
        return cached[1]
    data = await _rcon_json(server, 'stats api list true')
    if not data.get('ok'):
        return cached[1] if cached is not None else []
    items = data.get('scoreboards')
    if not isinstance(items, list):
        return []
    _LIST_CACHE[server_key] = (now, items)
    return items


def _build_scoreboard_embed(client: DisManagerClient, data: dict[str, Any]) -> discord.Embed:
    display_name = str(data.get('displayName') or data.get('id') or 'Scoreboard')
    obj_id = str(data.get('id') or '')
    criterion = str(data.get('criterion') or 'dummy')
    page = int(data.get('page') or 1)
    max_page = int(data.get('maxPage') or 1)
    total_entries = int(data.get('totalEntries') or 0)
    total_enabled = bool(data.get('totalEnabled'))
    total_val = int(data.get('total') or 0)
    entries = data.get('entries') or []

    embed = discord.Embed(
        title=f'> {display_name}',
        colour=0x2B2D31,
    )

    logo_url = _get_logo_url(client)
    if logo_url:
        embed.set_author(name='Aeternum SMP', icon_url=logo_url)

    ranks: list[str] = []
    owners: list[str] = []
    scores: list[str] = []

    if total_enabled:
        ranks.append('**0.**')
        owners.append('**Total**')
        scores.append(f'**{total_val:,}**')

    for row in entries:
        ranks.append(f"`{int(row.get('rank') or 0)}.`")
        owners.append(str(row.get('owner') or '?')[:22])
        scores.append(f"`{int(row.get('score') or 0):,}`")

    if ranks:
        embed.add_field(name='#', value='\n'.join(ranks), inline=True)
        embed.add_field(name='Jugador', value='\n'.join(owners), inline=True)
        embed.add_field(name='Valor', value='\n'.join(scores), inline=True)
    else:
        embed.description = '*Sin entradas para mostrar.*'

    footer_text = f'Página {page}/{max_page} · {total_entries} registros · {obj_id} ({criterion})'
    if logo_url:
        embed.set_footer(text=footer_text, icon_url=logo_url)
    else:
        embed.set_footer(text=footer_text)
    return embed


class ScoreboardView(discord.ui.View):
    """Paginated scoreboard viewer using RCON JSON endpoints."""

    def __init__(
        self,
        client: DisManagerClient,
        *,
        mode: str,
        target: str,
        category: str = '',
        page: int = 1,
        max_page: int = 1,
    ) -> None:
        super().__init__(timeout=300)
        self.client = client
        self.mode = mode
        self.target = target
        self.category = category
        self.page = page
        self.max_page = max_page
        self._rebuild_buttons()

    def _build_command(self, page: int) -> str:
        if self.mode == 'stat':
            return f'stats api stat {self.category} {self.target} {page} {PAGE_SIZE}'
        return f'stats api get {self.target} {page} {PAGE_SIZE}'

    def _rebuild_buttons(self) -> None:
        self.clear_items()
        if self.max_page > 1:
            if self.max_page > 2:
                self.add_item(_PageButton('<<', target_page=1, disabled=self.page <= 1))
            self.add_item(_PageButton('<', target_page=max(1, self.page - 1), disabled=self.page <= 1))
            self.add_item(_PageButton('>', target_page=min(self.max_page, self.page + 1), disabled=self.page >= self.max_page))
            if self.max_page > 2:
                self.add_item(_PageButton('>>', target_page=self.max_page, disabled=self.page >= self.max_page))
        self.add_item(_RefreshButton())

    async def load_page(self, page: int) -> tuple[discord.Embed | None, str | None]:
        resolved = _resolve_server(self.client)
        if resolved is None:
            return None, '✖ Servidor no encontrado o desconectado.'
        _, srv = resolved
        data = await _rcon_json(srv, self._build_command(page))
        if not data.get('ok'):
            return None, f"✖ {data.get('error', 'No se pudo consultar la scoreboard.')}"
        self.page = int(data.get('page') or 1)
        self.max_page = int(data.get('maxPage') or 1)
        self._rebuild_buttons()
        return _build_scoreboard_embed(self.client, data), None

    async def navigate(self, interaction: discord.Interaction, page: int) -> None:
        if not interaction.response.is_done():
            await interaction.response.defer()
        embed, err = await self.load_page(page)
        if err is not None or embed is None:
            await interaction.followup.send(err or '✖ Error al actualizar.', ephemeral=True)
            return
        if interaction.message is not None:
            await interaction.followup.edit_message(
                message_id=interaction.message.id,
                embed=embed,
                view=self,
            )


class _PageButton(discord.ui.Button[ScoreboardView]):
    def __init__(self, label: str, *, target_page: int, disabled: bool) -> None:
        super().__init__(label=label, style=discord.ButtonStyle.gray, row=0, disabled=disabled)
        self._target_page = target_page

    async def callback(self, interaction: discord.Interaction) -> None:
        assert self.view is not None
        await self.view.navigate(interaction, self._target_page)


class _RefreshButton(discord.ui.Button[ScoreboardView]):
    def __init__(self) -> None:
        super().__init__(label='🔄', style=discord.ButtonStyle.gray, row=0)

    async def callback(self, interaction: discord.Interaction) -> None:
        assert self.view is not None
        await self.view.navigate(interaction, self.view.page)


class ScoreboardCommandCog(commands.Cog):
    """Slash commands to inspect scoreboards and stats via RCON."""

    scoreboard_group = app_commands.Group(
        name='scoreboard',
        description='Consulta scoreboards y stats del servidor',
        guild_only=True,
    )

    def __init__(self, client: DisManagerClient) -> None:
        self.client = client

    async def _objective_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> list[Choice[str]]:
        resolved = _resolve_server(self.client)
        if resolved is None:
            return []
        key, srv = resolved
        items = await _fetch_objectives_cached(key, srv)
        needle = current.casefold()
        choices: list[Choice[str]] = []
        for item in items:
            obj_id = str(item.get('id') or '')
            disp = str(item.get('displayName') or obj_id)
            if needle and needle not in obj_id.casefold() and needle not in disp.casefold():
                continue
            label = disp if disp == obj_id else f'{disp} ({obj_id})'
            choices.append(Choice(name=label[:100], value=obj_id[:100]))
            if len(choices) >= 25:
                break
        return choices

    @scoreboard_group.command(name='ver', description='Muestra una scoreboard existente con paginado')
    @app_commands.describe(objetivo='Scoreboard a consultar')
    @app_commands.autocomplete(objetivo=_objective_autocomplete)
    async def ver_command(
        self,
        interaction: discord.Interaction,
        objetivo: str,
    ) -> None:
        await interaction.response.defer()
        if _resolve_server(self.client) is None:
            await interaction.followup.send('✖ No hay servidor disponible.', ephemeral=True)
            return
        view = ScoreboardView(self.client, mode='get', target=objetivo)
        embed, err = await view.load_page(1)
        if err is not None or embed is None:
            await interaction.followup.send(err or '✖ Error al consultar scoreboard.', ephemeral=True)
            return
        await interaction.followup.send(embed=embed, view=view)

    @scoreboard_group.command(name='stat', description='Consulta cualquier stat técnica de Minecraft (ej. stone_slab)')
    @app_commands.describe(
        categoria='Categoría de stat',
        stat='ID técnico en Minecraft (ej. obsidian, stone_slab, play_time)',
    )
    @app_commands.choices(categoria=[Choice(name=c, value=c) for c in _STAT_CATEGORIES])
    async def stat_command(
        self,
        interaction: discord.Interaction,
        categoria: Choice[str],
        stat: str,
    ) -> None:
        await interaction.response.defer()
        if _resolve_server(self.client) is None:
            await interaction.followup.send('✖ No hay servidor disponible.', ephemeral=True)
            return
        clean_stat = stat.strip().removeprefix('minecraft:').lower()
        view = ScoreboardView(
            self.client,
            mode='stat',
            category=categoria.value,
            target=clean_stat,
        )
        embed, err = await view.load_page(1)
        if err is not None or embed is None:
            await interaction.followup.send(err or '✖ Error al consultar stat.', ephemeral=True)
            return
        await interaction.followup.send(embed=embed, view=view)


async def setup(client: DisManagerClient) -> None:
    """Register the ScoreboardCommandCog on ``client``."""
    await client.add_cog(ScoreboardCommandCog(client))
