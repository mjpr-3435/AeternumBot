from __future__ import annotations

import math
from datetime import date
from typing import cast

import discord
from Classes.config import get_ae_config
from dismanager.classes import DisManagerClient
from Utils.discord_helpers import get_or_create_thread, is_admin
from Utils.minecraft_api import mc_uuid

from .Store import (
    add_to_mc_whitelist,
    filter_whitelist_rows,
    load_whitelist_rows,
    parse_iso_date,
    purge_inactive_whitelist_entries,
    remove_from_mc_whitelist,
    save_whitelist_rows,
    update_whitelist_on_servers,
)


def _has_interviewer_role(client: DisManagerClient, user: discord.abc.User) -> bool:
    role_id = get_ae_config(client).tickets.interviewer_role_id
    return isinstance(user, discord.Member) and any(role.id == role_id for role in user.roles)


def _format_last_connection_date(date_value: str, *, relative_dates: bool) -> str:
    if not relative_dates:
        return date_value
    parsed = parse_iso_date(date_value)
    if parsed is None:
        return date_value
    days = max(0, (date.today() - parsed).days)
    return 'hace 1 dia' if days == 1 else f'hace {days} dias'


def _message_is_inactives_mode(message: discord.Message | None) -> bool:
    if message is None or not message.embeds:
        return False
    footer_text = message.embeds[0].footer.text or ''
    return 'Inactives' in footer_text


def _message_uses_relative_dates(message: discord.Message | None) -> bool:
    if message is None or not message.embeds:
        return True
    footer_text = message.embeds[0].footer.text or ''
    return 'Fecha' not in footer_text


def _format_nickname_list(names: list[str], limit: int = 25) -> str:
    if not names:
        return 'Ninguno'
    shown = names[:limit]
    text = ', '.join(shown)
    if len(names) > limit:
        text += f', ... (+{len(names) - limit})'
    return text


def _make_whitelist_log_embed(
    client: DisManagerClient,
    content: str,
    nickname: str,
    edited_by: str,
) -> discord.Embed:
    mc_uuid_online = mc_uuid(player=nickname, online=True)
    mc_uuid_offline = mc_uuid(player=nickname, online=False)
    icon_url = client.user.display_avatar.url if client.user is not None else None

    return (
        discord.Embed(
            title='> **Whitelist SMP**',
            description=(
                f'{content}\n'
                f'- **Username:** {nickname}\n'
                f"- **Online UUID:** {mc_uuid_online if mc_uuid_online is not None else 'El usuario no es Premium.'}\n"
                f'- **Offline UUID:** {mc_uuid_offline}\n'
                f'Editado por: {edited_by}\n'
            ),
            color=0x2F3136,
        )
        .set_thumbnail(url=f'https://mc-heads.net/head/{nickname.lower()}.png')
        .set_footer(text='Whitelist System \u200b', icon_url=icon_url)
    )


def whitelist_embed(
    client: DisManagerClient,
    page: int = 1,
    page_size: int = 30,
    *,
    inactives_only: bool = False,
    relative_dates: bool = True,
) -> discord.Embed:
    """Build a paginated whitelist embed."""
    rows = filter_whitelist_rows(inactives_only=inactives_only)
    start = (page - 1) * page_size
    page_rows = rows[start : start + page_size]

    if not page_rows:
        show_nick = '`---`'
        show_user = '`---`'
        show_date = '`---`'
    else:
        show_nick = '\n'.join(
            f"`{row['index'] + 1:>3}`‎ ‎ ‎ `{row['nickname'][:16]:>16}`" for row in page_rows
        )
        show_user = '\n'.join(f"`🧧` <@{row['user_id']}>" for row in page_rows)
        show_date = '\n'.join(
            f"`📆` {_format_last_connection_date(row['date'], relative_dates=relative_dates)}"
            for row in page_rows
        )

    footer_mode = 'Inactives' if inactives_only else 'All'
    footer_date_mode = 'Dias' if relative_dates else 'Fecha'
    return (
        discord.Embed(color=0x2F3136)
        .set_footer(
            icon_url=get_ae_config(client).thumbnail,
            text=f'Aeternum Whitelist | {footer_mode} | {footer_date_mode}',
        )
        .add_field(inline=True, name='`  #`‎ ‎ ‎ **Usuario**', value=f'\n{show_nick}')
        .add_field(inline=True, name='**Añadido Por**', value=f'\n{show_user}')
        .add_field(inline=True, name='**Última Conexión**', value=f'\n{show_date}')
    )


class AddNicknameModal(discord.ui.Modal, title='Agregar a la Whitelist'):
    """Modal to add a Minecraft player to the whitelist."""

    nickname: discord.ui.TextInput[AddNicknameModal]

    def __init__(self) -> None:
        super().__init__()
        self.nickname = discord.ui.TextInput(required=True)
        self.add_item(
            discord.ui.Label(
                text='Nickname (Considera mayúsculas y minúsculas)',
                component=self.nickname,
            )
        )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True, thinking=True)
        client = cast(DisManagerClient, interaction.client)
        nickname = self.nickname.value.replace(' ', '')
        rows = load_whitelist_rows()
        inactives_only = _message_is_inactives_mode(interaction.message)
        relative_dates = _message_uses_relative_dates(interaction.message)

        if any(row['nickname'] == nickname for row in rows):
            embed = _make_whitelist_log_embed(
                client,
                'El usuario ya estaba en la whitelist.',
                nickname,
                interaction.user.mention,
            )
            await interaction.followup.send(embed=embed)
            return

        rows.append({
            'index': len(rows),
            'nickname': nickname,
            'user_id': interaction.user.id,
            'date': 'No Registrado',
        })
        rows.sort(key=lambda item: item['nickname'].casefold())
        save_whitelist_rows(rows)
        add_to_mc_whitelist(nickname)
        update_whitelist_on_servers(client)

        embed = _make_whitelist_log_embed(client, 'Usuario añadido.', nickname, interaction.user.mention)
        await interaction.followup.send(embed=embed)
        if interaction.message is not None:
            await interaction.followup.edit_message(
                message_id=interaction.message.id,
                embed=whitelist_embed(
                    client,
                    inactives_only=inactives_only,
                    relative_dates=relative_dates,
                ),
            )

        channel = client.get_channel(get_ae_config(client).members_info.channel_id)
        if isinstance(channel, discord.TextChannel):
            log_thread = await get_or_create_thread('Whitelist Log', channel)
            await log_thread.send(embed=embed)


class RemoveNicknameModal(discord.ui.Modal, title='Remover de la Whitelist'):
    """Modal to remove a Minecraft player from the whitelist."""

    nickname: discord.ui.TextInput[RemoveNicknameModal]

    def __init__(self) -> None:
        super().__init__()
        self.nickname = discord.ui.TextInput(required=True)
        self.add_item(
            discord.ui.Label(
                text='Nickname (Considera mayúsculas y minúsculas)',
                component=self.nickname,
            )
        )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True, thinking=True)
        client = cast(DisManagerClient, interaction.client)
        nickname = self.nickname.value.strip()
        rows = load_whitelist_rows()
        inactives_only = _message_is_inactives_mode(interaction.message)
        relative_dates = _message_uses_relative_dates(interaction.message)

        if not any(row['nickname'] == nickname for row in rows):
            embed = _make_whitelist_log_embed(
                client,
                'El usuario no estaba en la whitelist.',
                nickname,
                interaction.user.mention,
            )
            await interaction.followup.send(embed=embed)
            return

        save_whitelist_rows([row for row in rows if row['nickname'] != nickname])
        remove_from_mc_whitelist(nickname)
        update_whitelist_on_servers(client)

        embed = _make_whitelist_log_embed(client, 'Usuario removido.', nickname, interaction.user.mention)
        await interaction.followup.send(embed=embed)
        if interaction.message is not None:
            await interaction.followup.edit_message(
                message_id=interaction.message.id,
                embed=whitelist_embed(
                    client,
                    inactives_only=inactives_only,
                    relative_dates=relative_dates,
                ),
            )

        channel = client.get_channel(get_ae_config(client).members_info.channel_id)
        if isinstance(channel, discord.TextChannel):
            log_thread = await get_or_create_thread('Whitelist Log', channel)
            await log_thread.send(embed=embed)


class PurgeInactivesModal(discord.ui.Modal, title='Purge Inactives'):
    """Admin-only modal to purge inactive whitelist entries."""

    confirmation: discord.ui.TextInput[PurgeInactivesModal]
    exclusions: discord.ui.TextInput[PurgeInactivesModal]

    def __init__(self, whitelist_view: WhitelistListView) -> None:
        super().__init__()
        self.whitelist_view = whitelist_view
        self.confirmation = discord.ui.TextInput(
            placeholder='PURGE',
            required=True,
        )
        self.exclusions = discord.ui.TextInput(
            placeholder='Un nombre por línea:\nJugador1\nJugador2',
            required=False,
            style=discord.TextStyle.paragraph,
        )
        self.add_item(discord.ui.Label(text='Escribe PURGE para confirmar', component=self.confirmation))
        self.add_item(discord.ui.Label(text='Excluir nombres', component=self.exclusions))

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True, thinking=True)
        client = cast(DisManagerClient, interaction.client)

        if self.confirmation.value.strip().upper() != 'PURGE':
            await interaction.followup.send(
                '✖ Confirmación inválida. Debes escribir `PURGE`.',
                ephemeral=True,
            )
            return

        excluded_nicknames = [
            line.strip() for line in self.exclusions.value.splitlines() if line.strip()
        ]
        removed_nicknames, excluded_applied = purge_inactive_whitelist_entries(excluded_nicknames)
        update_whitelist_on_servers(client)

        if removed_nicknames:
            preview = ', '.join(removed_nicknames[:20])
            if len(removed_nicknames) > 20:
                preview += ', ...'
            extra = ''
            if excluded_applied:
                extra = f'\nExcluidos aplicados: **{len(excluded_applied)}**'
            elif excluded_nicknames:
                extra = (
                    f'\nExclusiones recibidas: **{len(excluded_nicknames)}** '
                    '(sin coincidencias inactivas)'
                )
            await interaction.followup.send(
                f'✔ Purge completado. Removidos: **{len(removed_nicknames)}**\n`{preview}`{extra}',
                ephemeral=True,
            )
        else:
            await interaction.followup.send('✔ No hay inactivos para eliminar.', ephemeral=True)

        channel = client.get_channel(get_ae_config(client).members_info.channel_id)
        if isinstance(channel, discord.TextChannel):
            log_thread = await get_or_create_thread('Whitelist Log', channel)
            icon_url = client.user.display_avatar.url if client.user is not None else None
            action_embed = discord.Embed(
                title='> **Whitelist SMP**',
                description=(
                    'Purge de inactivos ejecutado.\n'
                    f'- **Removidos:** {len(removed_nicknames)}\n'
                    f'- **Nombres removidos:** {_format_nickname_list(removed_nicknames)}\n'
                    f'- **Excluidos aplicados:** {_format_nickname_list(excluded_applied)}\n'
                    f'- **Editado por:** {interaction.user.mention}\n'
                ),
                color=0x2F3136,
            ).set_footer(text='Whitelist System \u200b', icon_url=icon_url)
            await log_thread.send(embed=action_embed)

        await self.whitelist_view.update_interface(interaction)


class _UpdateButton(discord.ui.Button['WhitelistListView']):
    def __init__(self) -> None:
        super().__init__(label='🔄', style=discord.ButtonStyle.gray, row=1)

    async def callback(self, interaction: discord.Interaction) -> None:
        assert self.view is not None
        await self.view.update_interface(interaction)


class _PreviousPageButton(discord.ui.Button['WhitelistListView']):
    def __init__(self) -> None:
        super().__init__(label='<', style=discord.ButtonStyle.gray, row=1)

    async def callback(self, interaction: discord.Interaction) -> None:
        assert self.view is not None
        self.view.page = max(1, self.view.page - 1)
        await self.view.update_interface(interaction)


class _NextPageButton(discord.ui.Button['WhitelistListView']):
    def __init__(self) -> None:
        super().__init__(label='>', style=discord.ButtonStyle.gray, row=1)

    async def callback(self, interaction: discord.Interaction) -> None:
        assert self.view is not None
        self.view.page = min(self.view.max_page, self.view.page + 1)
        await self.view.update_interface(interaction)


class _InactivesToggleButton(discord.ui.Button['WhitelistListView']):
    def __init__(self) -> None:
        super().__init__(label='All', style=discord.ButtonStyle.green, row=1)

    async def callback(self, interaction: discord.Interaction) -> None:
        assert self.view is not None
        if not isinstance(interaction.user, discord.Member) or not is_admin(interaction.user):
            await interaction.response.send_message(
                '✖ No tienes permisos.',
                ephemeral=True,
                delete_after=1,
            )
            return

        self.view.only_inactives = not self.view.only_inactives
        self.view.page = 1
        self.label = 'Inactives' if self.view.only_inactives else 'All'
        self.style = discord.ButtonStyle.gray if self.view.only_inactives else discord.ButtonStyle.green
        await self.view.update_interface(interaction)


class _DateFormatToggleButton(discord.ui.Button['WhitelistListView']):
    def __init__(self) -> None:
        super().__init__(label='Dias', style=discord.ButtonStyle.green, row=1)

    async def callback(self, interaction: discord.Interaction) -> None:
        assert self.view is not None
        if not isinstance(interaction.user, discord.Member) or not is_admin(interaction.user):
            await interaction.response.send_message(
                '✖ No tienes permisos.',
                ephemeral=True,
                delete_after=1,
            )
            return

        self.view.relative_dates = not self.view.relative_dates
        self.label = 'Dias' if self.view.relative_dates else 'Fecha'
        self.style = discord.ButtonStyle.green if self.view.relative_dates else discord.ButtonStyle.gray
        await self.view.update_interface(interaction)


class _WhitelistActionSelect(discord.ui.Select['WhitelistListView']):
    def __init__(self) -> None:
        options = [
            discord.SelectOption(label='Agregar', value='add', description='Añadir un usuario a la whitelist'),
            discord.SelectOption(
                label='Remover',
                value='remove',
                description='Eliminar un usuario de la whitelist',
            ),
            discord.SelectOption(
                label='Purgar',
                value='purge',
                description='Eliminar inactivos de la whitelist',
            ),
        ]
        super().__init__(
            placeholder='Acciones de whitelist',
            min_values=1,
            max_values=1,
            options=options,
            row=0,
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        assert self.view is not None
        client = cast(DisManagerClient, interaction.client)
        user_is_admin = isinstance(interaction.user, discord.Member) and is_admin(interaction.user)
        has_interviewer = _has_interviewer_role(client, interaction.user)
        action = self.values[0]

        if action == 'add':
            if not user_is_admin and not has_interviewer:
                await interaction.response.send_message('✖ No tienes permisos.', ephemeral=True, delete_after=1)
                return
            await interaction.response.send_modal(AddNicknameModal())
            return

        if action == 'remove':
            if not user_is_admin and not has_interviewer:
                await interaction.response.send_message('✖ No tienes permisos.', ephemeral=True, delete_after=1)
                return
            await interaction.response.send_modal(RemoveNicknameModal())
            return

        if action == 'purge':
            if not user_is_admin:
                await interaction.response.send_message('✖ No tienes permisos.', ephemeral=True, delete_after=1)
                return
            await interaction.response.send_modal(PurgeInactivesModal(self.view))


class WhitelistListView(discord.ui.View):
    """Ephemeral paginated whitelist viewer and management controls."""

    def __init__(self, *, is_admin_request: bool = False) -> None:
        super().__init__(timeout=300)
        self.is_admin_request = is_admin_request
        self.only_inactives = False
        self.relative_dates = True
        self.max_page = 1
        self.page = 1

        self._refresh_pagination()
        self.add_item(_UpdateButton())
        if self.is_admin_request:
            self.add_item(_InactivesToggleButton())
            self.add_item(_DateFormatToggleButton())
            self.add_item(_WhitelistActionSelect())
        self.add_item(_PreviousPageButton())
        self.add_item(_NextPageButton())

    def _refresh_pagination(self) -> None:
        total = len(filter_whitelist_rows(inactives_only=self.only_inactives))
        self.max_page = max(1, math.ceil(total / 30))
        self.page = min(max(self.page, 1), self.max_page)

    async def update_interface(self, interaction: discord.Interaction) -> None:
        self._refresh_pagination()
        if not interaction.response.is_done():
            await interaction.response.defer()
        if interaction.message is None:
            return
        client = cast(DisManagerClient, interaction.client)
        await interaction.followup.edit_message(
            message_id=interaction.message.id,
            embed=whitelist_embed(
                client,
                self.page,
                inactives_only=self.only_inactives,
                relative_dates=self.relative_dates,
            ),
            view=self,
        )
