from __future__ import annotations

import io
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import aiohttp
import discord
from Classes.config import AeternumConfigError, GitHubConfig, load_aeternum_config
from discord import app_commands
from discord.ext import commands
from dismanager.classes import DisManagerClient
from Utils.discord_helpers import is_admin

_ADDONS_ROOT = Path(__file__).resolve().parent.parent
_CONFIG_PATH = _ADDONS_ROOT / 'config.yml'
_GITHUB_API = 'https://api.github.com'
_ACCENT_COLOUR = 0x2ECC71

_PROTECTED_PREFIXES = (
    '.legacy/',
    '.ruff_cache/',
    '__pycache__/',
)

_PROTECTED_FILES = frozenset(
    {
        '.gitignore',
        'config.yml',
        'Banners/Public/HoneyPot/HoneyPotStats.json',
        'Banners/MembersInfo/Tasks/tasks.json',
        'Banners/MembersInfo/Whitelist/Whitelist.json',
        'Banners/MembersInfo/Whitelist/WhitelistLog.csv',
        'Banners/Public/Form/forms.json',
        'Banners/Public/TicketSystem/tickets.json',
        'MaterialLists/data.json',
    }
)


@dataclass(frozen=True, slots=True)
class _CommitInfo:
    sha: str
    author: str
    date_iso: str
    message: str


def _github_headers(token: str) -> dict[str, str]:
    headers = {
        'Accept': 'application/vnd.github+json',
        'User-Agent': 'AeternumBot-Updater',
        'X-GitHub-Api-Version': '2022-11-28',
    }
    if token:
        headers['Authorization'] = f'Bearer {token}'
    return headers


def _validate_github_config(gh: GitHubConfig) -> tuple[str, str, str]:
    repo = gh.repo.strip()
    if not repo or '/' not in repo or repo.count('/') != 1:
        raise ValueError('Configura `GitHub.Repo` (`owner/repo`) en `/config` primero.')
    branch = gh.branch.strip() or 'main'
    return repo, branch, gh.token.strip()


async def _fetch_latest_commit(repo: str, branch: str, token: str) -> _CommitInfo:
    url = f'{_GITHUB_API}/repos/{repo}/commits/{branch}'
    async with (
        aiohttp.ClientSession() as session,
        session.get(url, headers=_github_headers(token), timeout=aiohttp.ClientTimeout(total=15)) as resp,
    ):
        if resp.status != 200:
            detail = await resp.text()
            raise RuntimeError(f'GitHub API ({resp.status}): {detail[:300]}')
        data: dict[str, Any] = await resp.json()

    commit = data.get('commit', {})
    author_data = commit.get('author', {})
    raw_msg = str(commit.get('message', '')).strip()
    first_line = raw_msg.splitlines()[0] if raw_msg else '(sin mensaje)'
    return _CommitInfo(
        sha=str(data.get('sha', ''))[:7],
        author=str(author_data.get('name', 'desconocido')),
        date_iso=str(author_data.get('date', '')),
        message=first_line,
    )


async def _download_zipball(repo: str, branch: str, token: str) -> bytes:
    url = f'{_GITHUB_API}/repos/{repo}/zipball/{branch}'
    async with (
        aiohttp.ClientSession() as session,
        session.get(url, headers=_github_headers(token), timeout=aiohttp.ClientTimeout(total=60)) as resp,
    ):
        if resp.status != 200:
            detail = await resp.text()
            raise RuntimeError(f'Error descargando zipball ({resp.status}): {detail[:300]}')
        return await resp.read()


def _resolve_zip_prefix(names: list[str]) -> str:
    for name in names:
        if name.endswith('/AeternumBot/AeExtensions.py'):
            return name.removesuffix('AeExtensions.py')
    for name in names:
        parts = name.split('/', 1)
        if len(parts) == 2 and parts[1] == 'AeExtensions.py':
            return f'{parts[0]}/'
    raise RuntimeError('No se encontró `AeExtensions.py` dentro del zip de GitHub.')


def _is_protected(rel_posix: str) -> bool:
    if rel_posix in _PROTECTED_FILES:
        return True
    if any(rel_posix.startswith(prefix) for prefix in _PROTECTED_PREFIXES):
        return True
    return '/__pycache__/' in f'/{rel_posix}'


def _apply_zip_update(zip_bytes: bytes, target_root: Path) -> int:
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        names = [info.filename for info in archive.infolist() if not info.is_dir()]
        prefix = _resolve_zip_prefix(names)

        updated = 0
        for info in archive.infolist():
            if info.is_dir() or not info.filename.startswith(prefix):
                continue
            rel_posix = info.filename[len(prefix) :].lstrip('/')
            if not rel_posix or _is_protected(rel_posix):
                continue
            rel_path = Path(rel_posix)
            if rel_path.is_absolute() or '..' in rel_path.parts:
                continue

            dest = target_root / rel_path
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(archive.read(info.filename))
            updated += 1
        return updated


class _ApplyUpdateButton(discord.ui.Button['UpdateAddonsView']):
    def __init__(self) -> None:
        super().__init__(
            label='Actualizar y recargar',
            style=discord.ButtonStyle.success,
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        assert self.view is not None
        view = self.view
        await interaction.response.defer(ephemeral=True, thinking=True)
        try:
            zip_bytes = await _download_zipball(view.repo, view.branch, view.token)
            updated_files = _apply_zip_update(zip_bytes, _ADDONS_ROOT)
            reloaded = await view.client.reload_addons()
        except Exception as exc:
            await interaction.followup.send(
                f'❌ Error al actualizar: {exc}',
                ephemeral=True,
            )
            return

        await interaction.followup.send(
            f'✅ Actualizado `{view.repo}@{view.branch}` (`{view.commit.sha}`): '
            f'**{updated_files}** archivo(s) reemplazado(s) y **{reloaded}** addon(s) recargado(s).\n'
            f'> `config.yml` y registros locales preservados.',
            ephemeral=True,
        )


class UpdateAddonsView(discord.ui.LayoutView):
    """Confirmation banner showing the latest GitHub commit before applying an update."""

    def __init__(
        self,
        client: DisManagerClient,
        *,
        repo: str,
        branch: str,
        token: str,
        commit: _CommitInfo,
    ) -> None:
        super().__init__(timeout=180)
        self.client = client
        self.repo = repo
        self.branch = branch
        self.token = token
        self.commit = commit

        body = (
            f'## 🔄 Actualizar Addons desde GitHub\n'
            f'- **Repositorio:** `{repo}` (`{branch}`)\n'
            f'- **Último commit:** `{commit.sha}` · {commit.author}\n'
            f'- **Fecha:** `{commit.date_iso}`\n'
            f'- **Mensaje:** {commit.message}\n\n'
            f'> Se preservarán `config.yml`, `.legacy/` y todos los registros locales (`.json` / `.csv`).'
        )
        self.add_item(
            discord.ui.Container(
                discord.ui.TextDisplay(body),
                discord.ui.Separator(),
                discord.ui.ActionRow(_ApplyUpdateButton()),
                accent_colour=_ACCENT_COLOUR,
            )
        )


class UpdateCommandCog(commands.Cog):
    """Admin-only ``/update addons`` command to pull updates from GitHub."""

    update_group = app_commands.Group(
        name='update',
        description='Actualiza componentes del bot desde GitHub.',
        default_permissions=discord.Permissions(administrator=True),
        guild_only=True,
    )

    def __init__(self, client: DisManagerClient) -> None:
        self.client = client

    @update_group.command(name='addons', description='Descarga la última versión de AeternumBot desde GitHub y recarga.')
    async def update_addons(self, interaction: discord.Interaction) -> None:
        if not isinstance(interaction.user, discord.Member) or not is_admin(interaction.user):
            await interaction.response.send_message(
                '❌ Solo administradores pueden usar `/update addons`.',
                ephemeral=True,
            )
            return

        try:
            cfg = load_aeternum_config(_CONFIG_PATH)
            repo, branch, token = _validate_github_config(cfg.github)
        except (ValueError, AeternumConfigError) as exc:
            await interaction.response.send_message(f'❌ {exc}', ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True, thinking=True)
        try:
            commit = await _fetch_latest_commit(repo, branch, token)
        except Exception as exc:
            await interaction.followup.send(f'❌ No se pudo consultar GitHub: {exc}', ephemeral=True)
            return

        view = UpdateAddonsView(
            self.client,
            repo=repo,
            branch=branch,
            token=token,
            commit=commit,
        )
        await interaction.followup.send(view=view, ephemeral=True)


async def setup(client: DisManagerClient) -> None:
    """Register the UpdateCommandCog on ``client``."""
    await client.add_cog(UpdateCommandCog(client))
