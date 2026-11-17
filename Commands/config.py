from __future__ import annotations

from collections.abc import Callable
from datetime import date
from pathlib import Path
from typing import Any

import discord
from Classes.config import (
    AeternumConfig,
    AeternumConfigError,
    load_aeternum_config,
    save_aeternum_config_updates,
)
from discord import app_commands
from discord.ext import commands
from dismanager.classes import DisManagerClient
from Utils.discord_helpers import is_admin

_ADDONS_ROOT = Path(__file__).resolve().parent.parent
_CONFIG_PATH = _ADDONS_ROOT / 'config.yml'
_PLUGINS_DIR = _ADDONS_ROOT / 'Plugins'
_EMBED_COLOUR = 0x2F3136

_PAGE_TITLES = (
    'General',
    'Minecraft',
    'Servidores & Plugins',
    'Comunicación',
    'Seguridad (HoneyPot)',
    'Banners Públicos & Tickets',
    'MembersInfo',
)


def _fmt_str(value: str, *, spoiler: bool = False) -> str:
    if not value.strip():
        return '*Sin configurar*'
    return f'||{value}||' if spoiler else f'`{value}`'


def _fmt_channel(channel_id: int) -> str:
    return f'<#{channel_id}> (`{channel_id}`)' if channel_id > 0 else '*Sin configurar*'


def _fmt_role(role_id: int) -> str:
    return f'<@&{role_id}> (`{role_id}`)' if role_id > 0 else '*Sin configurar*'


def _fmt_list(values: tuple[str, ...]) -> str:
    if not values:
        return '*Sin configurar*'
    return ', '.join(f'`{item}`' for item in values)


def _parse_csv(raw: str) -> list[str]:
    return [part.strip() for part in raw.split(',') if part.strip()]


def _parse_hex_or_int(raw: str) -> int:
    text = raw.strip()
    if not text:
        return 0
    if text.startswith('#'):
        return int(text[1:], 16)
    if text.lower().startswith('0x'):
        return int(text, 16)
    return int(text, 10)


def _parse_non_negative_int(raw: str, *, maximum: int | None = None) -> int:
    text = raw.strip()
    if not text:
        return 0
    value = int(text)
    if value < 0:
        raise ValueError('El valor debe ser mayor o igual a 0.')
    if maximum is not None and value > maximum:
        raise ValueError(f'El valor máximo permitido es {maximum}.')
    return value


def _selected_id(values: list[Any]) -> int:
    return int(values[0].id) if values else 0


def _default_obj(item_id: int) -> list[discord.Object]:
    return [discord.Object(id=item_id)] if item_id > 0 else []


def _text_input(
    *,
    default: str,
    placeholder: str,
    max_length: int,
    style: discord.TextStyle = discord.TextStyle.short,
) -> discord.ui.TextInput[Any]:
    return discord.ui.TextInput(
        default=default,
        placeholder=placeholder,
        required=False,
        max_length=max_length,
        style=style,
    )


def _channel_select(
    channel_id: int,
    *,
    channel_types: list[discord.ChannelType],
) -> discord.ui.ChannelSelect[Any]:
    return discord.ui.ChannelSelect(
        channel_types=channel_types,
        default_values=_default_obj(channel_id),
        min_values=0,
        max_values=1,
        required=False,
    )


def _role_select(role_id: int) -> discord.ui.RoleSelect[Any]:
    return discord.ui.RoleSelect(
        default_values=_default_obj(role_id),
        min_values=0,
        max_values=1,
        required=False,
    )


def _multi_select(
    *,
    placeholder: str,
    options: list[discord.SelectOption],
) -> discord.ui.Select[Any]:
    return discord.ui.Select(
        placeholder=placeholder,
        options=options,
        min_values=0,
        max_values=len(options),
        required=False,
    )


def _available_plugin_files() -> list[str]:
    if not _PLUGINS_DIR.is_dir():
        return []
    return sorted(path.name for path in _PLUGINS_DIR.iterdir() if path.is_file() and path.suffix == '.py')


def _available_processes(client: DisManagerClient, cfg: AeternumConfig) -> list[str]:
    names = [proc.name for proc in client.processes]
    for server_name in cfg.servers:
        if server_name not in names:
            names.append(server_name)
    return names


# =========================================
#                  Modals
# =========================================


class _BaseConfigModal(discord.ui.Modal):
    def __init__(
        self,
        *,
        title: str,
        banner_view: ConfigBannerView,
        section_label: str,
    ) -> None:
        super().__init__(title=title)
        self.banner_view = banner_view
        self.section_label = section_label

    def build_updates(self) -> dict[str, Any]:
        raise NotImplementedError

    async def on_submit(self, interaction: discord.Interaction) -> None:
        try:
            updates = self.build_updates()
            new_cfg = save_aeternum_config_updates(_CONFIG_PATH, updates)
        except (ValueError, AeternumConfigError) as exc:
            await interaction.response.send_message(
                f'✖ Error de validación: {exc}',
                ephemeral=True,
            )
            return

        self.banner_view.cfg = new_cfg
        self.banner_view.rebuild()
        await interaction.response.edit_message(
            embed=self.banner_view.build_embed(),
            view=self.banner_view,
        )
        await interaction.followup.send(
            f'✔ **{self.section_label}** guardado en `config.yml`. '
            'Ejecuta `!!adreload` cuando termines para aplicar los cambios.',
            ephemeral=True,
        )


class GeneralModal(_BaseConfigModal):
    def __init__(self, banner_view: ConfigBannerView) -> None:
        super().__init__(
            title='General',
            banner_view=banner_view,
            section_label='General',
        )
        cfg = banner_view.cfg
        self.thumbnail_input = _text_input(
            default=cfg.thumbnail,
            placeholder='https://...',
            max_length=300,
        )
        self.emoji_input = _text_input(
            default=cfg.server_emoji,
            placeholder='<:aeternum:123456789>',
            max_length=120,
        )
        self.add_item(discord.ui.Label(text='Thumbnail URL', component=self.thumbnail_input))
        self.add_item(discord.ui.Label(text='Server Emoji', component=self.emoji_input))

    def build_updates(self) -> dict[str, Any]:
        return {
            'Thumbnail': self.thumbnail_input.value.strip(),
            'Server Emoji': self.emoji_input.value.strip(),
        }


class MinecraftModal(_BaseConfigModal):
    def __init__(self, banner_view: ConfigBannerView) -> None:
        super().__init__(
            title='Minecraft',
            banner_view=banner_view,
            section_label='Minecraft',
        )
        cfg = banner_view.cfg
        self.rcon_input = _text_input(
            default=cfg.rcon_password,
            placeholder='Contraseña RCON',
            max_length=120,
        )
        self.version_input = _text_input(
            default=cfg.minecraft_version,
            placeholder='Java 1.21.4',
            max_length=40,
        )
        self.admins_input = _text_input(
            default='\n'.join(cfg.admins),
            placeholder='Un nombre por línea:\nJugador1\nJugador2',
            max_length=500,
            style=discord.TextStyle.paragraph,
        )
        self.operator_input = _text_input(
            default=cfg.world_trimmer.operator,
            placeholder='Jugador operador de WorldTrimmer',
            max_length=64,
        )
        self.add_item(discord.ui.Label(text='RCON Password', component=self.rcon_input))
        self.add_item(discord.ui.Label(text='Minecraft Version', component=self.version_input))
        self.add_item(
            discord.ui.Label(
                text='Admins (Minecraft)',
                description='Un nombre por línea.',
                component=self.admins_input,
            )
        )
        self.add_item(discord.ui.Label(text='WorldTrimmer Operator', component=self.operator_input))

    def build_updates(self) -> dict[str, Any]:
        return {
            'RCON Password': self.rcon_input.value.strip(),
            'Minecraft Version': self.version_input.value.strip(),
            'Admins': [line.strip() for line in self.admins_input.value.splitlines() if line.strip()],
            'WorldTrimmer': {'Operator': self.operator_input.value.strip()},
        }


class GitHubModal(_BaseConfigModal):
    def __init__(self, banner_view: ConfigBannerView) -> None:
        super().__init__(
            title='GitHub Updater',
            banner_view=banner_view,
            section_label='GitHub Updater',
        )
        gh = banner_view.cfg.github
        self.repo_input = _text_input(
            default=gh.repo,
            placeholder='owner/repo',
            max_length=120,
        )
        self.branch_input = _text_input(
            default=gh.branch,
            placeholder='main',
            max_length=80,
        )
        self.token_input = _text_input(
            default=gh.token,
            placeholder='github_pat_... (solo lectura Contents)',
            max_length=250,
        )
        self.add_item(discord.ui.Label(text='Repo (owner/repo)', component=self.repo_input))
        self.add_item(discord.ui.Label(text='Branch', component=self.branch_input))
        self.add_item(
            discord.ui.Label(
                text='Token (PAT)',
                description='Opcional: solo necesario para repositorios privados.',
                component=self.token_input,
            )
        )

    def build_updates(self) -> dict[str, Any]:
        repo = self.repo_input.value.strip()
        if repo and ('/' not in repo or repo.count('/') != 1):
            raise ValueError('Repo debe tener formato owner/repo.')
        return {
            'GitHub': {
                'Repo': repo,
                'Branch': self.branch_input.value.strip(),
                'Token': self.token_input.value.strip(),
            }
        }


class ServersTargetsModal(_BaseConfigModal):
    def __init__(self, banner_view: ConfigBannerView) -> None:
        super().__init__(
            title='Servers & Guide Targets',
            banner_view=banner_view,
            section_label='Servers & Guide Targets',
        )
        cfg = banner_view.cfg
        processes = _available_processes(banner_view.client, cfg)
        self.servers_select: discord.ui.Select[Any] | None = None
        self.guides_select: discord.ui.Select[Any] | None = None
        self.servers_input: discord.ui.TextInput[Any] | None = None
        self.guides_input: discord.ui.TextInput[Any] | None = None

        if processes:
            server_options = [
                discord.SelectOption(label=name, value=name, default=name in cfg.servers)
                for name in processes[:25]
            ]
            guide_options = [
                discord.SelectOption(label=name, value=name, default=name in cfg.guide_targets)
                for name in processes[:25]
            ]
            self.servers_select = discord.ui.Select(
                placeholder='Selecciona los procesos AeServer',
                options=server_options,
                min_values=0,
                max_values=len(server_options),
                required=False,
            )
            self.guides_select = discord.ui.Select(
                placeholder='Selecciona los destinos de Guides/',
                options=guide_options,
                min_values=0,
                max_values=len(guide_options),
                required=False,
            )
            self.add_item(discord.ui.Label(text='Servers', component=self.servers_select))
            self.add_item(discord.ui.Label(text='Guide Targets', component=self.guides_select))
        else:
            self.servers_input = discord.ui.TextInput(
                default=', '.join(cfg.servers),
                placeholder='SMP, CMP, MMP, PMP',
                required=False,
                max_length=300,
            )
            self.guides_input = discord.ui.TextInput(
                default=', '.join(cfg.guide_targets),
                placeholder='SMP, CMP, MMP',
                required=False,
                max_length=300,
            )
            self.add_item(
                discord.ui.Label(
                    text='Servers',
                    description='Nombres separados por coma.',
                    component=self.servers_input,
                )
            )
            self.add_item(
                discord.ui.Label(
                    text='Guide Targets',
                    description='Nombres separados por coma.',
                    component=self.guides_input,
                )
            )

    def build_updates(self) -> dict[str, Any]:
        if self.servers_select is not None and self.guides_select is not None:
            servers = list(self.servers_select.values)
            guides = list(self.guides_select.values)
        else:
            assert self.servers_input is not None and self.guides_input is not None
            servers = _parse_csv(self.servers_input.value)
            guides = _parse_csv(self.guides_input.value)
        return {
            'Servers': servers,
            'Guide Targets': guides,
        }


class ServerPluginsModal(_BaseConfigModal):
    def __init__(self, banner_view: ConfigBannerView, server_name: str) -> None:
        super().__init__(
            title=f'Plugins: {server_name}'[:45],
            banner_view=banner_view,
            section_label=f'Plugins ({server_name})',
        )
        self.server_name = server_name
        current = set(banner_view.cfg.plugins.get(server_name, ()))
        plugin_files = _available_plugin_files()
        options = [
            discord.SelectOption(label=name, value=name, default=name in current)
            for name in plugin_files[:25]
        ]
        self.plugins_select = _multi_select(
            placeholder=f'Plugins activos para {server_name}',
            options=options,
        )
        self.add_item(
            discord.ui.Label(
                text=f'Plugins para {server_name}',
                description='Se copiarán a <proceso>/.plugins/ al cargar.',
                component=self.plugins_select,
            )
        )

    def build_updates(self) -> dict[str, Any]:
        return {'Plugins': {self.server_name: list(self.plugins_select.values)}}


class CommunicationModal(_BaseConfigModal):
    def __init__(self, banner_view: ConfigBannerView) -> None:
        super().__init__(
            title='Comunicación (ChatBridge & TTS)',
            banner_view=banner_view,
            section_label='Comunicación',
        )
        cfg = banner_view.cfg
        self.cb_channel = _channel_select(
            cfg.chatbridge.channel_id,
            channel_types=[discord.ChannelType.text],
        )
        self.cb_webhook = _text_input(
            default=cfg.chatbridge.webhook_name,
            placeholder='ChatBridge',
            max_length=80,
        )
        self.tts_channel = _channel_select(
            cfg.tts.channel_id,
            channel_types=[discord.ChannelType.text],
        )
        self.tts_webhook = _text_input(
            default=cfg.tts.webhook_name,
            placeholder='TTs Extra',
            max_length=80,
        )
        self.add_item(discord.ui.Label(text='ChatBridge: Canal', component=self.cb_channel))
        self.add_item(discord.ui.Label(text='ChatBridge: Webhook Name', component=self.cb_webhook))
        self.add_item(discord.ui.Label(text='TTS: Canal', component=self.tts_channel))
        self.add_item(discord.ui.Label(text='TTS: Webhook Name', component=self.tts_webhook))

    def build_updates(self) -> dict[str, Any]:
        return {
            'ChatBridge': {
                'Channel ID': _selected_id(self.cb_channel.values),
                'Webhook Name': self.cb_webhook.value.strip(),
            },
            'TTS': {
                'Channel ID': _selected_id(self.tts_channel.values),
                'Webhook Name': self.tts_webhook.value.strip(),
            },
        }


class HoneyPotModal(_BaseConfigModal):
    def __init__(self, banner_view: ConfigBannerView) -> None:
        super().__init__(
            title='Seguridad (HoneyPot)',
            banner_view=banner_view,
            section_label='HoneyPot',
        )
        hp = banner_view.cfg.honeypot
        self.channel_select = _channel_select(
            hp.channel_id,
            channel_types=[discord.ChannelType.text],
        )
        self.accent_input = _text_input(
            default=f'0x{hp.accent_color:06X}' if hp.accent_color > 0 else '',
            placeholder='0xF2B632',
            max_length=16,
        )
        self.reason_input = _text_input(
            default=hp.ban_reason,
            placeholder='HoneyPot triggered: message sent in restricted security channel.',
            max_length=300,
        )
        self.delete_hours_input = _text_input(
            default=str(hp.delete_message_hours) if hp.delete_message_hours > 0 else '',
            placeholder='24',
            max_length=4,
        )

        self.add_item(discord.ui.Label(text='Canal HoneyPot', component=self.channel_select))
        self.add_item(discord.ui.Label(text='Accent Color (hex)', component=self.accent_input))
        self.add_item(discord.ui.Label(text='Ban Reason', component=self.reason_input))
        self.add_item(
            discord.ui.Label(
                text='Delete Message Hours',
                description='Entre 0 y 168 horas (máx. 7 días).',
                component=self.delete_hours_input,
            )
        )

    def build_updates(self) -> dict[str, Any]:
        return {
            'HoneyPot': {
                'Channel ID': _selected_id(self.channel_select.values),
                'Accent Color': _parse_hex_or_int(self.accent_input.value),
                'Ban Reason': self.reason_input.value.strip(),
                'Delete Message Hours': _parse_non_negative_int(
                    self.delete_hours_input.value,
                    maximum=168,
                ),
            }
        }


class InterviewersTicketsModal(_BaseConfigModal):
    def __init__(self, banner_view: ConfigBannerView) -> None:
        super().__init__(
            title='InterviewersInfo & Tickets',
            banner_view=banner_view,
            section_label='InterviewersInfo & Tickets',
        )
        cfg = banner_view.cfg
        self.interviewers_channel = _channel_select(
            cfg.interviewers_info.channel_id,
            channel_types=[discord.ChannelType.text],
        )
        self.interviewer_role = _role_select(cfg.tickets.interviewer_role_id)
        self.add_item(discord.ui.Label(text='Canal InterviewersInfo', component=self.interviewers_channel))
        self.add_item(discord.ui.Label(text='Rol Interviewer (Tickets)', component=self.interviewer_role))

    def build_updates(self) -> dict[str, Any]:
        return {
            'InterviewersInfo': {'Channel ID': _selected_id(self.interviewers_channel.values)},
            'Tickets': {'Interviewer Role ID': _selected_id(self.interviewer_role.values)},
        }


class DiscordInfoChannelsModal(_BaseConfigModal):
    def __init__(self, banner_view: ConfigBannerView) -> None:
        super().__init__(
            title='DiscordInfo: Canales y Categoría',
            banner_view=banner_view,
            section_label='DiscordInfo (Canales)',
        )
        di = banner_view.cfg.discord_info
        self.info_channel = _channel_select(
            di.channel_id,
            channel_types=[discord.ChannelType.text],
        )
        self.showcase_channel = _channel_select(
            di.showcase_id,
            channel_types=[discord.ChannelType.text, discord.ChannelType.forum],
        )
        self.forms_channel = _channel_select(
            di.forms_channel_id,
            channel_types=[discord.ChannelType.text],
        )
        self.tickets_category = _channel_select(
            di.tickets_category_id,
            channel_types=[discord.ChannelType.category],
        )
        self.add_item(discord.ui.Label(text='Canal DiscordInfo', component=self.info_channel))
        self.add_item(discord.ui.Label(text='Canal Showcase', component=self.showcase_channel))
        self.add_item(discord.ui.Label(text='Canal Forms', component=self.forms_channel))
        self.add_item(discord.ui.Label(text='Categoría Tickets', component=self.tickets_category))

    def build_updates(self) -> dict[str, Any]:
        return {
            'DiscordInfo': {
                'Channel ID': _selected_id(self.info_channel.values),
                'Showcase ID': _selected_id(self.showcase_channel.values),
                'Forms Channel ID': _selected_id(self.forms_channel.values),
                'Tickets Category ID': _selected_id(self.tickets_category.values),
            }
        }


class DiscordInfoServerModal(_BaseConfigModal):
    def __init__(self, banner_view: ConfigBannerView) -> None:
        super().__init__(
            title='DiscordInfo: Server Info',
            banner_view=banner_view,
            section_label='DiscordInfo (Server Info)',
        )
        di = banner_view.cfg.discord_info
        self.host_input = _text_input(
            default=di.host_info,
            placeholder='Tipo:: Servidor Dedicado\nUbicación:: ...\nRAM:: 64 GB DDR5',
            max_length=1000,
            style=discord.TextStyle.paragraph,
        )
        self.rules_input = _text_input(
            default=di.carpet_rules,
            placeholder='AccurateBlockPlacement\nInstamineDeepslate\nCombineXPOrbs',
            max_length=1000,
            style=discord.TextStyle.paragraph,
        )
        self.mods_input = _text_input(
            default=di.server_mods,
            placeholder='Syncmatica\nEssentialCarefulBreak\nStarlight',
            max_length=1000,
            style=discord.TextStyle.paragraph,
        )
        self.add_item(discord.ui.Label(text='Host Info (asciidoc)', component=self.host_input))
        self.add_item(
            discord.ui.Label(
                text='Carpet Rules',
                description='Una regla por línea.',
                component=self.rules_input,
            )
        )
        self.add_item(
            discord.ui.Label(
                text='Server Mods',
                description='Un mod por línea.',
                component=self.mods_input,
            )
        )

    def build_updates(self) -> dict[str, Any]:
        return {
            'DiscordInfo': {
                'Host Info': self.host_input.value.strip(),
                'Carpet Rules': self.rules_input.value.strip(),
                'Server Mods': self.mods_input.value.strip(),
            }
        }


class DiscordInfoLinksModal(_BaseConfigModal):
    def __init__(self, banner_view: ConfigBannerView) -> None:
        super().__init__(
            title='DiscordInfo: Links',
            banner_view=banner_view,
            section_label='DiscordInfo (Links)',
        )
        di = banner_view.cfg.discord_info
        self.links_input = _text_input(
            default='\n'.join(di.links),
            placeholder='Overviewer,🌐,https://...\nYouTube,<:AeYoutube:...>,https://...',
            max_length=1500,
            style=discord.TextStyle.paragraph,
        )
        self.add_item(
            discord.ui.Label(
                text='Links (nombre,emoji,url)',
                description='Una línea por link. Usa {invite} para la invitación de Discord.',
                component=self.links_input,
            )
        )

    def build_updates(self) -> dict[str, Any]:
        parsed: list[str] = []
        for idx, raw_line in enumerate(self.links_input.value.splitlines(), start=1):
            line = raw_line.strip()
            if not line:
                continue
            parts = [part.strip() for part in line.split(',', 2)]
            if len(parts) != 3 or not parts[0] or not parts[2]:
                raise ValueError(f'Línea {idx} inválida. Formato requerido: nombre,emoji,url')
            parsed.append(f'{parts[0]},{parts[1]},{parts[2]}')
        return {'DiscordInfo': {'Links': parsed}}


class DiscordInfoDetailsModal(_BaseConfigModal):
    def __init__(self, banner_view: ConfigBannerView) -> None:
        super().__init__(
            title='DiscordInfo: Datos y Emojis',
            banner_view=banner_view,
            section_label='DiscordInfo (Datos)',
        )
        di = banner_view.cfg.discord_info
        self.foundation_input = _text_input(
            default=di.foundation_date,
            placeholder='YYYY-MM-DD',
            max_length=20,
        )
        self.invite_input = _text_input(
            default=di.invite,
            placeholder='https://discord.gg/...',
            max_length=200,
        )
        self.emoji_yes_input = _text_input(
            default=di.form_emoji_yes,
            placeholder='<:PepeYes:...>',
            max_length=120,
        )
        self.emoji_no_input = _text_input(
            default=di.form_emoji_no,
            placeholder='<:PepeNo:...>',
            max_length=120,
        )
        self.add_item(discord.ui.Label(text='Foundation Date (YYYY-MM-DD)', component=self.foundation_input))
        self.add_item(discord.ui.Label(text='Invite URL', component=self.invite_input))
        self.add_item(discord.ui.Label(text='Form Emoji Yes', component=self.emoji_yes_input))
        self.add_item(discord.ui.Label(text='Form Emoji No', component=self.emoji_no_input))

    def build_updates(self) -> dict[str, Any]:
        foundation = self.foundation_input.value.strip()
        if foundation:
            date.fromisoformat(foundation)
        return {
            'DiscordInfo': {
                'Foundation Date': foundation,
                'Invite': self.invite_input.value.strip(),
                'Form Emoji Yes': self.emoji_yes_input.value.strip(),
                'Form Emoji No': self.emoji_no_input.value.strip(),
            }
        }


class MembersInfoMainModal(_BaseConfigModal):
    def __init__(self, banner_view: ConfigBannerView) -> None:
        super().__init__(
            title='MembersInfo: Canal e IPs',
            banner_view=banner_view,
            section_label='MembersInfo (Canal e IPs)',
        )
        mi = banner_view.cfg.members_info
        self.channel_select = _channel_select(
            mi.channel_id,
            channel_types=[discord.ChannelType.text],
        )
        self.ip_server_input = _text_input(
            default=mi.ip_server,
            placeholder='mc.ejemplo.net',
            max_length=150,
        )
        self.ip_plugins_input = _text_input(
            default=mi.ip_plugins,
            placeholder='plugins.ejemplo.net',
            max_length=150,
        )
        self.add_item(discord.ui.Label(text='Canal MembersInfo', component=self.channel_select))
        self.add_item(discord.ui.Label(text='IP Server', component=self.ip_server_input))
        self.add_item(discord.ui.Label(text='IP Plugins', component=self.ip_plugins_input))

    def build_updates(self) -> dict[str, Any]:
        return {
            'MembersInfo': {
                'Channel ID': _selected_id(self.channel_select.values),
                'IP Server': self.ip_server_input.value.strip(),
                'IP Plugins': self.ip_plugins_input.value.strip(),
            }
        }


class MembersInfoExtraModal(_BaseConfigModal):
    def __init__(self, banner_view: ConfigBannerView) -> None:
        super().__init__(
            title='MembersInfo: Seed, PayPal & Twitch',
            banner_view=banner_view,
            section_label='MembersInfo (Extras)',
        )
        mi = banner_view.cfg.members_info
        self.seed_input = _text_input(
            default=mi.seed,
            placeholder='Seed del mundo',
            max_length=64,
        )
        self.paypal_input = _text_input(
            default=mi.paypal_link,
            placeholder='https://paypal.me/...',
            max_length=200,
        )
        self.twitch_input = _text_input(
            default=mi.twitch_stream_key,
            placeholder='live_...',
            max_length=200,
        )
        self.add_item(discord.ui.Label(text='Seed', component=self.seed_input))
        self.add_item(discord.ui.Label(text='Paypal Link', component=self.paypal_input))
        self.add_item(discord.ui.Label(text='Twitch Stream Key', component=self.twitch_input))

    def build_updates(self) -> dict[str, Any]:
        return {
            'MembersInfo': {
                'Seed': self.seed_input.value.strip(),
                'Paypal Link': self.paypal_input.value.strip(),
                'Twitch Stream Key': self.twitch_input.value.strip(),
            }
        }


# =========================================
#            Banner & Pagination
# =========================================


class _PrevPageButton(discord.ui.Button['ConfigBannerView']):
    def __init__(self, *, disabled: bool) -> None:
        super().__init__(
            label='<',
            style=discord.ButtonStyle.secondary,
            disabled=disabled,
            row=2,
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        assert self.view is not None
        view = self.view
        view.page = max(0, view.page - 1)
        view.rebuild()
        await interaction.response.edit_message(
            embed=view.build_embed(),
            view=view,
        )


class _NextPageButton(discord.ui.Button['ConfigBannerView']):
    def __init__(self, *, disabled: bool) -> None:
        super().__init__(
            label='>',
            style=discord.ButtonStyle.secondary,
            disabled=disabled,
            row=2,
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        assert self.view is not None
        view = self.view
        view.page = min(len(_PAGE_TITLES) - 1, view.page + 1)
        view.rebuild()
        await interaction.response.edit_message(
            embed=view.build_embed(),
            view=view,
        )


class _PageSelect(discord.ui.Select['ConfigBannerView']):
    def __init__(self, current_page: int) -> None:
        options = [
            discord.SelectOption(
                label=f'{idx + 1}. {title}',
                value=str(idx),
                default=idx == current_page,
            )
            for idx, title in enumerate(_PAGE_TITLES)
        ]
        super().__init__(
            placeholder='Ir a la página...',
            min_values=1,
            max_values=1,
            options=options,
            row=0,
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        assert self.view is not None
        view = self.view
        view.page = int(self.values[0])
        view.rebuild()
        await interaction.response.edit_message(
            embed=view.build_embed(),
            view=view,
        )


def _make_plugins_modal_factory(
    server_name: str,
) -> Callable[[ConfigBannerView], discord.ui.Modal]:
    def _factory(view: ConfigBannerView) -> discord.ui.Modal:
        return ServerPluginsModal(view, server_name)

    return _factory


class _EditSectionSelect(discord.ui.Select['ConfigBannerView']):
    def __init__(
        self,
        options: list[discord.SelectOption],
        modal_factories: dict[str, Callable[[ConfigBannerView], discord.ui.Modal]],
    ) -> None:
        super().__init__(
            placeholder='Selecciona un bloque para editar...',
            min_values=1,
            max_values=1,
            options=options,
            row=1,
        )
        self.modal_factories = modal_factories

    async def callback(self, interaction: discord.Interaction) -> None:
        assert self.view is not None
        factory = self.modal_factories.get(self.values[0])
        if factory is None:
            await interaction.response.send_message('✖ Bloque desconocido.', ephemeral=True)
            return
        await interaction.response.send_modal(factory(self.view))


class ConfigBannerView(discord.ui.View):
    """Paginated configuration banner for ``AeternumBot/config.yml``."""

    def __init__(self, client: DisManagerClient, cfg: AeternumConfig) -> None:
        super().__init__(timeout=600)
        self.client = client
        self.cfg = cfg
        self.page = 0
        self.rebuild()

    def _page_body(self) -> str:
        cfg = self.cfg
        if self.page == 0:
            gh = cfg.github
            token_txt = f'||{gh.token}||' if gh.token.strip() else '*Opcional (solo repos privados)*'
            return (
                f'- **Thumbnail:** {_fmt_str(cfg.thumbnail)}\n'
                f'- **Server Emoji:** {_fmt_str(cfg.server_emoji)}\n\n'
                f'**GitHub Updater**\n'
                f'- **Repo:** {_fmt_str(gh.repo)}\n'
                f'- **Branch:** {_fmt_str(gh.branch)}\n'
                f'- **Token:** {token_txt}'
            )
        if self.page == 1:
            return (
                f'- **RCON Password:** {_fmt_str(cfg.rcon_password, spoiler=True)}\n'
                f'- **Minecraft Version:** {_fmt_str(cfg.minecraft_version)}\n'
                f'- **Admins:** {_fmt_list(cfg.admins)}\n'
                f'- **WorldTrimmer Operator:** {_fmt_str(cfg.world_trimmer.operator)}'
            )
        if self.page == 2:
            processes = _available_processes(self.client, cfg)
            plugin_lines = [
                f'  - `{srv}`: {_fmt_list(cfg.plugins.get(srv, ()))}'
                for srv in (processes or list(cfg.plugins))
            ]
            plugins_text = '\n'.join(plugin_lines) if plugin_lines else '  - *Sin servidores detectados*'
            return (
                f'- **Servers:** {_fmt_list(cfg.servers)}\n'
                f'- **Guide Targets:** {_fmt_list(cfg.guide_targets)}\n'
                f'- **Plugins por servidor:**\n{plugins_text}'
            )
        if self.page == 3:
            return (
                f'**ChatBridge**\n'
                f'- **Channel ID:** {_fmt_channel(cfg.chatbridge.channel_id)}\n'
                f'- **Webhook Name:** {_fmt_str(cfg.chatbridge.webhook_name)}\n\n'
                f'**TTS**\n'
                f'- **Channel ID:** {_fmt_channel(cfg.tts.channel_id)}\n'
                f'- **Webhook Name:** {_fmt_str(cfg.tts.webhook_name)}'
            )
        if self.page == 4:
            hp = cfg.honeypot
            color_txt = f'`0x{hp.accent_color:06X}`' if hp.accent_color > 0 else '*Sin configurar*'
            del_txt = f'`{hp.delete_message_hours}h`' if hp.delete_message_hours > 0 else '`0h`'
            return (
                f'- **Channel ID:** {_fmt_channel(hp.channel_id)}\n'
                f'- **Accent Color:** {color_txt}\n'
                f'- **Ban Reason:** {_fmt_str(hp.ban_reason)}\n'
                f'- **Delete Message Hours:** {del_txt}'
            )
        if self.page == 5:
            di = cfg.discord_info
            links_txt = f'`{len(di.links)} link(s)`' if di.links else '*Sin configurar*'
            host_txt = '`Configurado`' if di.host_info.strip() else '*Sin configurar*'
            rules_txt = '`Configurado`' if di.carpet_rules.strip() else '*Sin configurar*'
            mods_txt = '`Configurado`' if di.server_mods.strip() else '*Sin configurar*'
            return (
                f'**InterviewersInfo & Tickets**\n'
                f'- **InterviewersInfo Channel:** {_fmt_channel(cfg.interviewers_info.channel_id)}\n'
                f'- **Interviewer Role:** {_fmt_role(cfg.tickets.interviewer_role_id)}\n\n'
                f'**DiscordInfo**\n'
                f'- **Channel ID:** {_fmt_channel(di.channel_id)}\n'
                f'- **Showcase ID:** {_fmt_channel(di.showcase_id)}\n'
                f'- **Forms Channel ID:** {_fmt_channel(di.forms_channel_id)}\n'
                f'- **Tickets Category ID:** {_fmt_channel(di.tickets_category_id)}\n'
                f'- **Foundation Date:** {_fmt_str(di.foundation_date)}\n'
                f'- **Invite:** {_fmt_str(di.invite)}\n'
                f'- **Form Emoji Yes / No:** {_fmt_str(di.form_emoji_yes)} / {_fmt_str(di.form_emoji_no)}\n'
                f'- **Links:** {links_txt}\n'
                f'- **Server Info (Host / Carpet / Mods):** {host_txt} / {rules_txt} / {mods_txt}'
            )
        mi = cfg.members_info
        return (
            f'- **Channel ID:** {_fmt_channel(mi.channel_id)}\n'
            f'- **IP Server:** {_fmt_str(mi.ip_server)}\n'
            f'- **IP Plugins:** {_fmt_str(mi.ip_plugins)}\n'
            f'- **Seed:** {_fmt_str(mi.seed)}\n'
            f'- **Paypal Link:** {_fmt_str(mi.paypal_link)}\n'
            f'- **Twitch Stream Key:** {_fmt_str(mi.twitch_stream_key, spoiler=True)}'
        )

    def _page_select(self) -> _EditSectionSelect:
        if self.page == 0:
            options = [
                discord.SelectOption(
                    label='General',
                    value='general',
                    description='Thumbnail y Server Emoji',
                ),
                discord.SelectOption(
                    label='GitHub Updater',
                    value='github',
                    description='Repo, Branch y Token para /update addons',
                ),
            ]
            factories: dict[str, Callable[[ConfigBannerView], discord.ui.Modal]] = {
                'general': GeneralModal,
                'github': GitHubModal,
            }
            return _EditSectionSelect(options, factories)

        if self.page == 1:
            return _EditSectionSelect(
                [
                    discord.SelectOption(
                        label='Minecraft',
                        value='minecraft',
                        description='RCON Password, Version, Admins y WorldTrimmer Operator',
                    )
                ],
                {'minecraft': MinecraftModal},
            )

        if self.page == 2:
            options = [
                discord.SelectOption(
                    label='Servers & Guide Targets',
                    value='servers_targets',
                    description='Procesos activos y sincronización de guías',
                )
            ]
            factories = {'servers_targets': ServersTargetsModal}
            plugin_files = _available_plugin_files()
            if plugin_files:
                for server_name in _available_processes(self.client, self.cfg)[:24]:
                    key = f'plugins:{server_name}'
                    options.append(
                        discord.SelectOption(
                            label=f'Plugins: {server_name}'[:100],
                            value=key,
                            description=f'Elegir plugins para {server_name}'[:100],
                        )
                    )
                    factories[key] = _make_plugins_modal_factory(server_name)
            return _EditSectionSelect(options, factories)

        if self.page == 3:
            return _EditSectionSelect(
                [
                    discord.SelectOption(
                        label='ChatBridge & TTS',
                        value='comm',
                        description='Canales y webhooks de ChatBridge y TTS',
                    )
                ],
                {'comm': CommunicationModal},
            )

        if self.page == 4:
            return _EditSectionSelect(
                [
                    discord.SelectOption(
                        label='HoneyPot',
                        value='honeypot',
                        description='Canal, color, motivo y borrado',
                    )
                ],
                {'honeypot': HoneyPotModal},
            )

        if self.page == 5:
            return _EditSectionSelect(
                [
                    discord.SelectOption(
                        label='InterviewersInfo & Tickets',
                        value='interviewers_tickets',
                        description='Canal de Interviewers y rol Interviewer',
                    ),
                    discord.SelectOption(
                        label='DiscordInfo: Canales y Categoría',
                        value='discord_channels',
                        description='Channel, Showcase, Forms y Tickets Category',
                    ),
                    discord.SelectOption(
                        label='DiscordInfo: Datos y Emojis',
                        value='discord_details',
                        description='Foundation Date, Invite y Form Emojis',
                    ),
                    discord.SelectOption(
                        label='DiscordInfo: Links',
                        value='discord_links',
                        description='Links en formato nombre,emoji,url (uno por línea)',
                    ),
                    discord.SelectOption(
                        label='DiscordInfo: Server Info',
                        value='discord_server',
                        description='Host Info, Carpet Rules y Server Mods',
                    ),
                ],
                {
                    'interviewers_tickets': InterviewersTicketsModal,
                    'discord_channels': DiscordInfoChannelsModal,
                    'discord_details': DiscordInfoDetailsModal,
                    'discord_links': DiscordInfoLinksModal,
                    'discord_server': DiscordInfoServerModal,
                },
            )

        return _EditSectionSelect(
            [
                discord.SelectOption(
                    label='MembersInfo: Canal e IPs',
                    value='members_main',
                    description='Canal, IP Server e IP Plugins',
                ),
                discord.SelectOption(
                    label='MembersInfo: Seed, PayPal & Twitch',
                    value='members_extra',
                    description='Seed, enlace PayPal y Twitch Stream Key',
                ),
            ],
            {
                'members_main': MembersInfoMainModal,
                'members_extra': MembersInfoExtraModal,
            },
        )

    def build_embed(self) -> discord.Embed:
        embed = discord.Embed(
            title=_PAGE_TITLES[self.page],
            description=self._page_body(),
            colour=_EMBED_COLOUR,
        )
        embed.set_footer(text=f'Página {self.page + 1}/{len(_PAGE_TITLES)}')
        return embed

    def rebuild(self) -> None:
        self.clear_items()
        self.add_item(_PageSelect(self.page))
        self.add_item(self._page_select())
        self.add_item(_PrevPageButton(disabled=self.page == 0))
        self.add_item(_NextPageButton(disabled=self.page == len(_PAGE_TITLES) - 1))


# =========================================
#                  Cog
# =========================================


class ConfigCommandCog(commands.Cog):
    """Admin-only slash command to inspect and edit ``AeternumBot/config.yml``."""

    def __init__(self, client: DisManagerClient) -> None:
        self.client = client

    @app_commands.command(name='config', description='Configura AeternumBot desde un panel interactivo.')
    @app_commands.default_permissions(administrator=True)
    @app_commands.guild_only()
    async def config_command(self, interaction: discord.Interaction) -> None:
        if not isinstance(interaction.user, discord.Member) or not is_admin(interaction.user):
            await interaction.response.send_message(
                '✖ Solo administradores pueden usar `/config`.',
                ephemeral=True,
            )
            return

        try:
            cfg = load_aeternum_config(_CONFIG_PATH)
        except AeternumConfigError as exc:
            await interaction.response.send_message(
                f'✖ No se pudo leer `config.yml`: {exc}',
                ephemeral=True,
            )
            return

        view = ConfigBannerView(self.client, cfg)
        await interaction.response.send_message(embed=view.build_embed(), view=view, ephemeral=True)


async def setup(client: DisManagerClient) -> None:
    """Register the ConfigCommandCog on ``client``."""
    await client.add_cog(ConfigCommandCog(client))
