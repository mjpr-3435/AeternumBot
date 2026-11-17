from __future__ import annotations

from collections.abc import Mapping, MutableMapping
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypeGuard, cast

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap
from ruamel.yaml.error import YAMLError

if TYPE_CHECKING:
    from Classes.AeServer import AeServer
    from dismanager.classes import DisManagerClient


class AeternumConfigError(Exception):
    """Raised when ``AeternumBot/config.yml`` cannot be read or is invalid."""


@dataclass(frozen=True, slots=True)
class GitHubConfig:
    """GitHub repository settings for ``/update addons``."""

    repo: str
    branch: str
    token: str


@dataclass(frozen=True, slots=True)
class ChatBridgeConfig:
    """ChatBridge channel and webhook settings."""

    channel_id: int
    webhook_name: str


@dataclass(frozen=True, slots=True)
class TtsConfig:
    """TTS relay channel and webhook settings."""

    channel_id: int
    webhook_name: str


@dataclass(frozen=True, slots=True)
class TicketsConfig:
    """Application ticket permissions and settings."""

    interviewer_role_id: int


@dataclass(frozen=True, slots=True)
class WorldTrimmerConfig:
    """Offline world-trimmer operator settings."""

    operator: str


@dataclass(frozen=True, slots=True)
class HoneyPotConfig:
    """HoneyPot moderation and logging settings."""

    channel_id: int
    accent_color: int
    ban_reason: str
    delete_message_hours: int


@dataclass(frozen=True, slots=True)
class InterviewersInfoConfig:
    """InterviewersInfo banner channel settings."""

    channel_id: int


@dataclass(frozen=True, slots=True)
class DiscordInfoConfig:
    """DiscordInfo, Showcase, Form, and TicketSystem channel/category settings."""

    channel_id: int
    foundation_date: str
    invite: str
    showcase_id: int
    forms_channel_id: int
    form_emoji_yes: str
    form_emoji_no: str
    tickets_category_id: int
    links: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class MembersInfoConfig:
    """MembersInfo banner and server metadata settings."""

    channel_id: int
    ip_server: str
    ip_plugins: str
    seed: str
    paypal_link: str
    twitch_stream_key: str


@dataclass(frozen=True, slots=True)
class AeternumConfig:
    """Centralized validated configuration for AeternumBot."""

    rcon_password: str
    minecraft_version: str
    thumbnail: str
    server_emoji: str
    github: GitHubConfig
    admins: tuple[str, ...]
    servers: tuple[str, ...]
    guide_targets: tuple[str, ...]
    chatbridge: ChatBridgeConfig
    tts: TtsConfig
    tickets: TicketsConfig
    world_trimmer: WorldTrimmerConfig
    honeypot: HoneyPotConfig
    interviewers_info: InterviewersInfoConfig
    discord_info: DiscordInfoConfig
    members_info: MembersInfoConfig
    plugins: dict[str, tuple[str, ...]]


def load_aeternum_config(path: Path) -> AeternumConfig:
    """Load and validate ``AeternumConfig`` from a YAML file at ``path``."""
    yaml = YAML(typ='safe')

    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_DEFAULT_CONFIG_YAML, encoding='utf-8')

    try:
        content = path.read_text(encoding='utf-8')
    except OSError as exc:
        raise AeternumConfigError(f"Could not read '{path}': {exc}") from exc

    try:
        raw: object = yaml.load(content)
    except YAMLError as exc:
        raise AeternumConfigError(f"Invalid YAML in '{path}': {exc}") from exc

    if not isinstance(raw, Mapping):
        raise AeternumConfigError('AeternumBot config root must be a YAML mapping.')

    return _build_aeternum_config(raw)


def save_aeternum_config_updates(path: Path, updates: Mapping[str, Any]) -> AeternumConfig:
    """Merge ``updates`` into ``path`` preserving comments, validate, and return the new config."""
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.indent(mapping=2, sequence=4, offset=2)

    try:
        content = path.read_text(encoding='utf-8')
    except OSError as exc:
        raise AeternumConfigError(f"Could not read '{path}': {exc}") from exc

    try:
        raw: object = yaml.load(content)
    except YAMLError as exc:
        raise AeternumConfigError(f"Invalid YAML in '{path}': {exc}") from exc

    if raw is None:
        raw = CommentedMap()
    if not isinstance(raw, MutableMapping):
        raise AeternumConfigError('AeternumBot config root must be a YAML mapping.')

    _deep_merge(raw, updates)
    validated = _build_aeternum_config(raw)

    buffer = StringIO()
    yaml.dump(raw, buffer)
    try:
        path.write_text(buffer.getvalue(), encoding='utf-8')
    except OSError as exc:
        raise AeternumConfigError(f"Could not write '{path}': {exc}") from exc

    return validated


def _build_aeternum_config(raw: Mapping[str, Any]) -> AeternumConfig:
    return AeternumConfig(
        rcon_password=_require_str(raw, 'RCON Password'),
        minecraft_version=_require_str(raw, 'Minecraft Version') if 'Minecraft Version' in raw else '',
        thumbnail=_require_str(raw, 'Thumbnail'),
        server_emoji=_require_str(raw, 'Server Emoji'),
        github=_parse_github(raw),
        admins=_require_str_tuple(raw, 'Admins'),
        servers=_require_str_tuple(raw, 'Servers'),
        guide_targets=_require_str_tuple(raw, 'Guide Targets'),
        chatbridge=_parse_chatbridge(raw),
        tts=_parse_tts(raw),
        tickets=_parse_tickets(raw),
        world_trimmer=_parse_world_trimmer(raw),
        honeypot=_parse_honeypot(raw),
        interviewers_info=_parse_interviewers_info(raw),
        discord_info=_parse_discord_info(raw),
        members_info=_parse_members_info(raw),
        plugins=_parse_plugins(raw),
    )


def _deep_merge(target: MutableMapping[str, Any], updates: Mapping[str, Any]) -> None:
    for key, value in updates.items():
        existing = target.get(key)
        if isinstance(value, Mapping) and isinstance(existing, MutableMapping):
            _deep_merge(existing, value)
        else:
            target[key] = dict(value) if isinstance(value, Mapping) else value


def get_ae_config(client: DisManagerClient) -> AeternumConfig:
    """Return the ``AeternumConfig`` attached to ``client``."""
    return cast(AeternumConfig, client.ae_config)  # type: ignore[attr-defined]


def get_ae_servers(client: DisManagerClient) -> dict[str, AeServer]:
    """Return the ``AeServer`` registry attached to ``client``."""
    return cast(dict[str, 'AeServer'], getattr(client, 'ae_servers', {}))


# =========================================
#            Internal Helpers
# =========================================


def _is_strict_int(value: object) -> TypeGuard[int]:
    return isinstance(value, int) and not isinstance(value, bool)


def _require_str(data: Mapping[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str):
        raise AeternumConfigError(f"'{key}' must be a string.")
    return value


def _require_int(data: Mapping[str, Any], key: str) -> int:
    value = data.get(key)
    if not _is_strict_int(value):
        raise AeternumConfigError(f"'{key}' must be an integer.")
    return value


def _require_mapping(data: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = data.get(key)
    if not isinstance(value, Mapping):
        raise AeternumConfigError(f"'{key}' must be a YAML mapping.")
    return value


def _require_str_tuple(data: Mapping[str, Any], key: str) -> tuple[str, ...]:
    value = data.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise AeternumConfigError(f"'{key}' must be a list of strings.")
    return tuple(value)


def _parse_chatbridge(data: Mapping[str, Any]) -> ChatBridgeConfig:
    chatbridge = _require_mapping(data, 'ChatBridge')
    return ChatBridgeConfig(
        channel_id=_require_int(chatbridge, 'Channel ID'),
        webhook_name=_require_str(chatbridge, 'Webhook Name'),
    )


def _parse_tts(data: Mapping[str, Any]) -> TtsConfig:
    tts = _require_mapping(data, 'TTS')
    return TtsConfig(
        channel_id=_require_int(tts, 'Channel ID'),
        webhook_name=_require_str(tts, 'Webhook Name'),
    )


def _parse_tickets(data: Mapping[str, Any]) -> TicketsConfig:
    tickets = _require_mapping(data, 'Tickets')
    return TicketsConfig(
        interviewer_role_id=_require_int(tickets, 'Interviewer Role ID'),
    )


def _parse_world_trimmer(data: Mapping[str, Any]) -> WorldTrimmerConfig:
    wt = _require_mapping(data, 'WorldTrimmer')
    return WorldTrimmerConfig(
        operator=_require_str(wt, 'Operator'),
    )


def _parse_honeypot(data: Mapping[str, Any]) -> HoneyPotConfig:
    hp = _require_mapping(data, 'HoneyPot')
    return HoneyPotConfig(
        channel_id=_require_int(hp, 'Channel ID'),
        accent_color=_require_int(hp, 'Accent Color'),
        ban_reason=_require_str(hp, 'Ban Reason'),
        delete_message_hours=_require_int(hp, 'Delete Message Hours'),
    )


def _parse_interviewers_info(data: Mapping[str, Any]) -> InterviewersInfoConfig:
    info = _require_mapping(data, 'InterviewersInfo')
    return InterviewersInfoConfig(
        channel_id=_require_int(info, 'Channel ID'),
    )


def _parse_discord_info(data: Mapping[str, Any]) -> DiscordInfoConfig:
    info = _require_mapping(data, 'DiscordInfo')
    return DiscordInfoConfig(
        channel_id=_require_int(info, 'Channel ID'),
        foundation_date=_require_str(info, 'Foundation Date'),
        invite=_require_str(info, 'Invite'),
        showcase_id=_require_int(info, 'Showcase ID'),
        forms_channel_id=_require_int(info, 'Forms Channel ID'),
        form_emoji_yes=_require_str(info, 'Form Emoji Yes'),
        form_emoji_no=_require_str(info, 'Form Emoji No'),
        tickets_category_id=_require_int(info, 'Tickets Category ID'),
        links=_require_str_tuple(info, 'Links') if 'Links' in info else (),
    )


def _parse_members_info(data: Mapping[str, Any]) -> MembersInfoConfig:
    info = _require_mapping(data, 'MembersInfo')
    return MembersInfoConfig(
        channel_id=_require_int(info, 'Channel ID'),
        ip_server=_require_str(info, 'IP Server'),
        ip_plugins=_require_str(info, 'IP Plugins'),
        seed=_require_str(info, 'Seed'),
        paypal_link=_require_str(info, 'Paypal Link'),
        twitch_stream_key=_require_str(info, 'Twitch Stream Key'),
    )


def _parse_github(data: Mapping[str, Any]) -> GitHubConfig:
    raw_gh = data.get('GitHub')
    if raw_gh is None:
        return GitHubConfig(repo='', branch='', token='')
    if not isinstance(raw_gh, Mapping):
        raise AeternumConfigError("'GitHub' must be a YAML mapping.")
    return GitHubConfig(
        repo=_require_str(raw_gh, 'Repo') if 'Repo' in raw_gh else '',
        branch=_require_str(raw_gh, 'Branch') if 'Branch' in raw_gh else '',
        token=_require_str(raw_gh, 'Token') if 'Token' in raw_gh else '',
    )


def _parse_plugins(data: Mapping[str, Any]) -> dict[str, tuple[str, ...]]:
    plugins = _require_mapping(data, 'Plugins')
    parsed: dict[str, tuple[str, ...]] = {}
    for server_name, entries in plugins.items():
        if not isinstance(server_name, str):
            raise AeternumConfigError("'Plugins' keys must be server names.")
        if not isinstance(entries, list) or not all(isinstance(item, str) for item in entries):
            raise AeternumConfigError(f"'Plugins.{server_name}' must be a list of strings.")
        parsed[server_name] = tuple(entries)
    return parsed


_DEFAULT_CONFIG_YAML = """# =========================================
#                 General
# =========================================

Thumbnail: ''
Server Emoji: ''

GitHub:
  Repo: ''
  Branch: ''
  Token: ''

# =========================================
#          Minecraft & Servidores
# =========================================

RCON Password: ''
Minecraft Version: ''

# Jugadores con permisos administrativos dentro de Minecraft
Admins: []

# Procesos de DisManager a los que se les crea una instancia AeServer
Servers: []

# Servidores que reciben la sincronización desde AeternumBot/Guides/
Guide Targets: []

WorldTrimmer:
  Operator: ''

# Plugins copiados a <proceso>/.plugins/ al cargar el addon
Plugins: {}

# =========================================
#              Comunicación
# =========================================

ChatBridge:
  Channel ID: 0
  Webhook Name: ''

TTS:
  Channel ID: 0
  Webhook Name: ''

# =========================================
#            Banners & Seguridad
# =========================================

HoneyPot:
  Channel ID: 0
  Accent Color: 0
  Ban Reason: ''
  Delete Message Hours: 0

InterviewersInfo:
  Channel ID: 0

DiscordInfo:
  Channel ID: 0
  Foundation Date: ''
  Invite: ''
  Showcase ID: 0
  Forms Channel ID: 0
  Form Emoji Yes: ''
  Form Emoji No: ''
  Tickets Category ID: 0
  Links: []

Tickets:
  Interviewer Role ID: 0

MembersInfo:
  Channel ID: 0
  IP Server: ''
  IP Plugins: ''
  Seed: ''
  Paypal Link: ''
  Twitch Stream Key: ''
"""
