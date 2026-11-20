from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import discord
from Classes.AeServer import AeServer
from Classes.config import get_ae_config, get_ae_servers
from dismanager.classes import BasePlugin, ManagedProcess

_LOG_MARKER = '[AeternumCarpet] [WE] '


class _SubStore:
    """Thread-safe/disk-backed per-perimeter Discord alert subscriptions (Ping and/or DM)."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.data: dict[str, dict[str, list[int]]] = {}
        self.load()

    def load(self) -> None:
        if not self.path.is_file():
            self.data = {}
            return
        try:
            raw = json.loads(self.path.read_text(encoding='utf-8'))
            if isinstance(raw, dict):
                self.data = {
                    str(k): {
                        'ping': list(v.get('ping', [])),
                        'dm': list(v.get('dm', [])),
                    }
                    for k, v in raw.items()
                    if isinstance(v, dict)
                }
        except Exception:
            self.data = {}

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, indent=2), encoding='utf-8')

    def subscribe(self, zone_key: str, mode: str, user_id: int) -> bool:
        entry = self.data.setdefault(zone_key, {'ping': [], 'dm': []})
        bucket = entry[mode]
        if user_id in bucket:
            return False
        bucket.append(user_id)
        self.save()
        return True

    def unsubscribe(self, zone_key: str, user_id: int) -> bool:
        entry = self.data.get(zone_key)
        if entry is None:
            return False
        changed = False
        for mode in ('ping', 'dm'):
            if user_id in entry[mode]:
                entry[mode].remove(user_id)
                changed = True
        if changed:
            self.save()
        return changed

    def subscribers(self, zone_key: str, mode: str) -> list[int]:
        entry = self.data.get(zone_key)
        return list(entry.get(mode, [])) if entry else []


def _extract_zone_key(interaction: discord.Interaction) -> str:
    msg = interaction.message
    if msg and msg.embeds:
        footer = msg.embeds[0].footer.text or ''
        if footer.startswith('WE:'):
            parts = footer.split(':', 2)
            if len(parts) == 3 and parts[2]:
                return parts[2]
    return 'global'


class WeSubscriptionView(discord.ui.View):
    """Persistent Discord embed buttons for managing per-perimeter Ping and DM alerts."""

    def __init__(self, store: _SubStore, allow_dm: bool) -> None:
        super().__init__(timeout=None)
        self.store = store
        self.allow_dm = allow_dm

    @discord.ui.button(
        label='Suscribir Ping',
        style=discord.ButtonStyle.success,
        custom_id='aeternum:we:ping',
    )
    async def sub_ping(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:
        zone = _extract_zone_key(interaction)
        added = self.store.subscribe(zone, 'ping', interaction.user.id)
        msg = (
            f'Suscrito a avisos por @ping en el canal para `{zone}`.'
            if added
            else f'Ya estabas suscrito a @ping para `{zone}`.'
        )
        await interaction.response.send_message(msg, ephemeral=True)

    @discord.ui.button(
        label='Suscribir DM',
        style=discord.ButtonStyle.primary,
        custom_id='aeternum:we:dm',
    )
    async def sub_dm(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:
        if not self.allow_dm:
            await interaction.response.send_message('Los avisos por DM están desactivados en config.', ephemeral=True)
            return
        zone = _extract_zone_key(interaction)
        added = self.store.subscribe(zone, 'dm', interaction.user.id)
        msg = (
            f'Suscrito a avisos personales por DM para `{zone}`.'
            if added
            else f'Ya estabas suscrito por DM para `{zone}`.'
        )
        await interaction.response.send_message(msg, ephemeral=True)

    @discord.ui.button(
        label='Desuscribirse',
        style=discord.ButtonStyle.secondary,
        custom_id='aeternum:we:unsub',
    )
    async def unsub(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:
        zone = _extract_zone_key(interaction)
        removed = self.store.unsubscribe(zone, interaction.user.id)
        msg = (
            f'Suscripción cancelada para `{zone}`.'
            if removed
            else f'No tenías suscripción activa para `{zone}`.'
        )
        await interaction.response.send_message(msg, ephemeral=True)


class plugin(BasePlugin):
    """Receives structured [AeternumCarpet] [WE] events and sends Discord embed/DM alerts."""

    process: ManagedProcess
    server: AeServer
    store: _SubStore
    view: WeSubscriptionView | None

    def __init__(self, process: ManagedProcess) -> None:
        self.process = process
        self.server = get_ae_servers(process.client)[process.name.casefold()]
        self.store = _SubStore(process.path / 'we_discord_subs.json')
        self.view = None

    async def on_plugins_load(self) -> None:
        cfg = get_ae_config(self.process.client)
        self.view = WeSubscriptionView(self.store, cfg.world_eater.allow_dm)
        self.process.client.add_view(self.view)

    async def on_process_log(self, log: str) -> None:
        idx = log.find(_LOG_MARKER)
        if idx < 0:
            return
        raw_json = log[idx + len(_LOG_MARKER) :].strip()
        try:
            payload = json.loads(raw_json)
        except json.JSONDecodeError:
            return
        if not isinstance(payload, dict):
            return
        await self._dispatch_event(payload)

    async def _dispatch_event(self, evt: dict[str, Any]) -> None:
        cfg = get_ae_config(self.process.client)
        channel_id = cfg.world_eater.channel_id
        if channel_id <= 0:
            return
        channel = self.process.client.get_channel(channel_id)
        if not isinstance(channel, discord.TextChannel):
            return

        event_type = str(evt.get('event', 'info'))
        zone_id = str(evt.get('id', 'global'))
        zone_name = str(evt.get('perimeter', zone_id))
        dimension = str(evt.get('dimension', 'overworld'))
        tnt_y = evt.get('tntY')
        target_y = evt.get('targetY')
        loaded_pct = evt.get('loadedPct', 0)
        active_bots = evt.get('activeBots')
        bounds = evt.get('bounds')
        hint = str(evt.get('hint', '') or '')

        titles = {
            'started': f'Vigilancia iniciada — {zone_name}',
            'active': f'World Eater en marcha — {zone_name}',
            'stalled': f'World Eater ATASCADO — {zone_name}',
            'low_y': f'World Eater en capas bajas — {zone_name}',
            'resumed': f'World Eater reanudado — {zone_name}',
            'unloaded': f'Zona descargada — {zone_name}',
            'stopped': f'Vigilancia detenida — {zone_name}',
        }
        descriptions = {
            'started': 'La vigilancia quedó activa y esperando las primeras detonaciones dentro del perímetro.',
            'active': 'Se detectaron detonaciones de TNT trabajando normalmente dentro del perímetro.',
            'stalled': 'No se han registrado detonaciones recientes dentro del tiempo configurado. Conviene revisar la máquina.',
            'low_y': 'Las detonaciones alcanzaron la altura objetivo configurada para este perímetro.',
            'resumed': 'Volvieron a detectarse detonaciones de TNT tras el atasco anterior.',
            'unloaded': 'Los chunks del perímetro quedaron descargados (`0%`), la vigilancia quedó en pausa.',
            'stopped': 'La vigilancia de este perímetro fue desactivada desde el panel.',
        }
        colors = {
            'started': 0x3FD8FF,
            'active': 0x4CAF50,
            'stalled': 0xFF5252,
            'low_y': 0xE0A95B,
            'resumed': 0x4CAF50,
            'unloaded': 0x9E9E9E,
            'stopped': 0x607D8B,
        }
        dim_labels = {
            'overworld': 'Overworld',
            'the_nether': 'Nether',
            'the_end': 'End',
        }
        dim_key = dimension.removeprefix('minecraft:')
        dim_label = dim_labels.get(dim_key, dim_key)

        embed = discord.Embed(
            title=titles.get(event_type, f'Evento World Eater ({event_type}) — {zone_name}'),
            description=descriptions.get(event_type, ''),
            color=colors.get(event_type, 0xE0A95B),
            timestamp=discord.utils.utcnow(),
        )
        embed.set_author(name='Aeternum • Monitor de World Eater')
        if cfg.thumbnail:
            embed.set_thumbnail(url=cfg.thumbnail)

        embed.add_field(name='Servidor', value=f'`{self.process.name}`', inline=True)
        embed.add_field(name='Dimensión', value=f'`{dim_label}`', inline=True)
        embed.add_field(name='Chunks cargados', value=f'`{loaded_pct}%`', inline=True)
        embed.add_field(
            name='Altura actual de TNT',
            value=f'`Y = {tnt_y}`' if tnt_y is not None else '`Sin detonaciones aún`',
            inline=True,
        )
        embed.add_field(name='Objetivo de excavación', value=f'`Y <= {target_y}`', inline=True)
        if active_bots is not None:
            embed.add_field(name='Bots en grilla', value=f'`{active_bots}`', inline=True)
        if isinstance(bounds, list) and len(bounds) == 4:
            embed.add_field(
                name='Área del perímetro',
                value=f'`[{bounds[0]}, {bounds[1]}]` → `[{bounds[2]}, {bounds[3]}]`',
                inline=False,
            )
        if hint:
            embed.add_field(name='Posible bloqueador cercano', value=f'`{hint}`', inline=False)
        embed.set_footer(
            text=f'WE:{self.process.name}:{zone_id}',
            icon_url=cfg.thumbnail or None,
        )

        critical = event_type in ('stalled', 'low_y', 'unloaded')
        mention_text = ''
        if critical:
            ping_ids = self.store.subscribers(zone_id, 'ping')
            if ping_ids:
                mention_text = ' '.join(f'<@{uid}>' for uid in ping_ids)

        view = self.view or discord.utils.MISSING
        await channel.send(content=mention_text or None, embed=embed, view=view)

        if critical and cfg.world_eater.allow_dm:
            for uid in self.store.subscribers(zone_id, 'dm'):
                user = self.process.client.get_user(uid)
                if user is None:
                    try:
                        user = await self.process.client.fetch_user(uid)
                    except discord.HTTPException:
                        user = None
                if user is not None:
                    try:
                        await user.send(embed=embed)
                    except discord.Forbidden:
                        pass
