from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import discord
from Classes.config import AeternumConfigError, load_aeternum_config
from discord import app_commands
from discord.ext import commands
from dismanager.classes import DisManagerClient
from Utils.discord_helpers import is_admin

_ADDONS_ROOT = Path(__file__).resolve().parent.parent
_CONFIG_PATH = _ADDONS_ROOT / 'config.yml'
_ACCENT_COLOUR = 0x2F3136


@dataclass(frozen=True, slots=True)
class _GitStatus:
    branch: str
    remote_ref: str
    local_sha: str
    remote_sha: str
    author: str
    date_iso: str
    message: str
    pending_commits: int


def _format_commit_date(date_iso: str) -> str:
    text = date_iso.strip()
    if not text:
        return '*Desconocida*'
    try:
        unix = int(datetime.fromisoformat(text).timestamp())
    except ValueError:
        return f'`{text}`'
    return f'<t:{unix}:f> (<t:{unix}:R>)'


async def _run_git(*args: str, timeout: float = 30.0) -> str:
    proc = await asyncio.create_subprocess_exec(
        'git',
        '-C',
        str(_ADDONS_ROOT),
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout_b, stderr_b = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except TimeoutError as exc:
        proc.kill()
        await proc.wait()
        raise RuntimeError(f'`git {args[0]}` excedió el tiempo límite ({int(timeout)}s).') from exc

    stdout = stdout_b.decode('utf-8', errors='replace').strip()
    stderr = stderr_b.decode('utf-8', errors='replace').strip()
    if proc.returncode != 0:
        detail = stderr or stdout or f'código {proc.returncode}'
        raise RuntimeError(f'`git {args[0]}` falló: {detail[:400]}')
    return stdout


async def _fetch_git_status(configured_branch: str) -> _GitStatus:
    branch = configured_branch.strip()
    if not branch:
        branch = await _run_git('rev-parse', '--abbrev-ref', 'HEAD')

    await _run_git('fetch', 'origin', branch, timeout=45.0)
    remote_ref = f'origin/{branch}'
    local_sha = await _run_git('rev-parse', '--short', 'HEAD')
    log_raw = await _run_git('log', '-1', '--format=%h%n%an%n%cI%n%s', remote_ref)
    lines = log_raw.splitlines()
    remote_sha = lines[0] if len(lines) > 0 else 'desconocido'
    author = lines[1] if len(lines) > 1 else 'desconocido'
    date_iso = lines[2] if len(lines) > 2 else ''
    message = lines[3] if len(lines) > 3 else '(sin mensaje)'
    pending_str = await _run_git('rev-list', '--count', f'HEAD..{remote_ref}')
    pending = int(pending_str) if pending_str.isdigit() else 0

    return _GitStatus(
        branch=branch,
        remote_ref=remote_ref,
        local_sha=local_sha,
        remote_sha=remote_sha,
        author=author,
        date_iso=date_iso,
        message=message,
        pending_commits=pending,
    )


class _ApplyUpdateButton(discord.ui.Button['UpdateAddonsView']):
    def __init__(self, *, pending: int) -> None:
        label = 'Actualizar y recargar' if pending > 0 else 'Recargar addons'
        super().__init__(
            label=label,
            style=discord.ButtonStyle.success if pending > 0 else discord.ButtonStyle.secondary,
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        assert self.view is not None
        view = self.view
        await interaction.response.defer(ephemeral=True, thinking=True)
        try:
            pull_output = await _run_git('pull', '--ff-only', 'origin', view.status.branch, timeout=60.0)
            new_sha = await _run_git('rev-parse', '--short', 'HEAD')
            reloaded = await view.client.reload_addons()
        except Exception as exc:
            await interaction.followup.send(
                f'✖ Error al actualizar: {exc}',
                ephemeral=True,
            )
            return

        summary_line = pull_output.splitlines()[-1] if pull_output else 'Actualizado.'
        await interaction.followup.send(
            f'✔ `{view.status.remote_ref}` (`{new_sha}`) · **{reloaded}** addon(s) recargado(s).\n'
            f'> `{summary_line}`',
            ephemeral=True,
        )


class UpdateAddonsView(discord.ui.LayoutView):
    """Confirmation banner showing git status before running ``git pull`` and reloading."""

    def __init__(self, client: DisManagerClient, *, status: _GitStatus) -> None:
        super().__init__(timeout=180)
        self.client = client
        self.status = status

        pending_label = (
            f'**{status.pending_commits}** commit(s) pendiente(s)'
            if status.pending_commits > 0
            else 'Al día (sin cambios pendientes)'
        )
        body = (
            f'## Actualizar Addons (`git pull`)\n'
            f'- **Rama:** `{status.branch}` (`{status.remote_ref}`)\n'
            f'- **Local:** `{status.local_sha}` → **Remoto:** `{status.remote_sha}` ({pending_label})\n'
            f'- **Autor:** {status.author}\n'
            f'- **Fecha:** {_format_commit_date(status.date_iso)}\n'
            f'- **Mensaje:** {status.message}\n\n'
            f'> `config.yml` y archivos ignorados en `.gitignore` se mantienen intactos.'
        )
        self.add_item(
            discord.ui.Container(
                discord.ui.TextDisplay(body),
                discord.ui.Separator(),
                discord.ui.ActionRow(_ApplyUpdateButton(pending=status.pending_commits)),
                accent_colour=_ACCENT_COLOUR,
            )
        )


class UpdateCommandCog(commands.Cog):
    """Admin-only ``/update addons`` command to pull updates via git and reload addons."""

    update_group = app_commands.Group(
        name='update',
        description='Actualiza componentes del bot desde git.',
        default_permissions=discord.Permissions(administrator=True),
        guild_only=True,
    )

    def __init__(self, client: DisManagerClient) -> None:
        self.client = client

    @update_group.command(name='addons', description='Hace git fetch/pull de AeternumBot y recarga los addons.')
    async def update_addons(self, interaction: discord.Interaction) -> None:
        if not isinstance(interaction.user, discord.Member) or not is_admin(interaction.user):
            await interaction.response.send_message(
                '✖ Solo administradores pueden usar `/update addons`.',
                ephemeral=True,
            )
            return

        branch = ''
        try:
            cfg = load_aeternum_config(_CONFIG_PATH)
            branch = cfg.github.branch
        except AeternumConfigError:
            pass

        await interaction.response.defer(ephemeral=True, thinking=True)
        try:
            status = await _fetch_git_status(branch)
        except Exception as exc:
            await interaction.followup.send(f'✖ No se pudo consultar git: {exc}', ephemeral=True)
            return

        view = UpdateAddonsView(self.client, status=status)
        await interaction.followup.send(view=view, ephemeral=True)


async def setup(client: DisManagerClient) -> None:
    """Register the UpdateCommandCog on ``client``."""
    await client.add_cog(UpdateCommandCog(client))
