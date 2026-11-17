"""Material-list cog and persistent UI views for AeternumBot."""

from __future__ import annotations

import asyncio
import io
import json
import uuid
from pathlib import Path
from typing import Any

import discord
from discord import app_commands
from discord.ext import commands
from dismanager.classes import DisManagerClient
from Utils.discord_helpers import is_admin

from .litematic_parser import export_to_carpet_csv, parse_litematic

ROOT = Path(__file__).parent
STATE_FILE = ROOT / 'data.json'
STATUS: dict[str, str] = {
    'claim': '📋',
    'done': '✅',
    'unclaim': '❌',
}


def _default_state() -> dict[str, Any]:
    return {'lists': {}}


def _short(value: str, size: int) -> str:
    return value if len(value) <= size else value[: size - 1] + '…'


def _format_section(item: dict[str, Any]) -> str:
    value = f"{item['status']} : {item['section']}"
    editor = item.get('edited_by')
    separator = ' - '
    author_length = 16 - len(value) - len(separator)
    if item['status'] in (STATUS['claim'], STATUS['done']) and editor and author_length > 0:
        value += separator + _short(str(editor), author_length)
    return _short(value, 16)


def _format_blocks(total: int) -> str:
    if total >= 1000:
        return f'{total:,}'.replace(',', '.')
    return str(total)


class Store:
    """Thread-safe JSON persistence for material lists."""

    def __init__(self) -> None:
        self.lock = asyncio.Lock()
        self.data: dict[str, Any] = _default_state()
        try:
            loaded = json.loads(STATE_FILE.read_text(encoding='utf-8'))
            if isinstance(loaded, dict):
                self.data.update(loaded)
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    async def save(self) -> None:
        async with self.lock:
            temporary = STATE_FILE.with_suffix('.tmp')
            temporary.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding='utf-8')
            temporary.replace(STATE_FILE)

    def get_list(self, list_id: str) -> dict[str, Any] | None:
        lists = self.data.get('lists', {})
        result = lists.get(list_id)
        return result if isinstance(result, dict) else None


class _ListNavButton(discord.ui.Button['ListView']):
    def __init__(self, addon: MaterialListsCog, list_id: str, label: str, action: str) -> None:
        super().__init__(
            label=label,
            style=discord.ButtonStyle.secondary,
            custom_id=f'material_lists:{list_id}:{action}',
        )
        self.addon = addon
        self.list_id = list_id
        self.action = action

    async def callback(self, interaction: discord.Interaction) -> None:
        record = self.addon.store.get_list(self.list_id)
        if not record or not record.get('active'):
            await interaction.response.send_message('Esta lista ya no está activa.', ephemeral=True)
            return
        pages = self.addon.page_count(record)
        page = int(record.get('page', 0))
        record['page'] = {
            'first': 0,
            'previous': max(0, page - 1),
            'next': min(pages - 1, page + 1),
            'last': pages - 1,
        }[self.action]
        await self.addon.store.save()
        await interaction.response.edit_message(
            embed=self.addon.embed(record),
            view=ListView(self.addon, self.list_id),
        )


class ListView(discord.ui.View):
    """Persistent pagination view for a material list embed."""

    def __init__(self, addon: MaterialListsCog, list_id: str) -> None:
        super().__init__(timeout=None)
        for label, action in (('≪', 'first'), ('‹', 'previous'), ('›', 'next'), ('≫', 'last')):
            self.add_item(_ListNavButton(addon, list_id, label, action))


class _EditorsNavButton(discord.ui.Button['EditorsView']):
    def __init__(
        self,
        addon: MaterialListsCog,
        record: dict[str, Any],
        label: str,
        target: int,
        *,
        disabled: bool,
    ) -> None:
        super().__init__(
            label=label,
            style=discord.ButtonStyle.secondary,
            disabled=disabled,
        )
        self.addon = addon
        self.record = record
        self.target = target

    async def callback(self, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(
            embed=self.addon.editors_embed(self.record, self.target),
            view=EditorsView(self.addon, self.record, self.target),
        )


class EditorsView(discord.ui.View):
    """Ephemeral pagination view listing who claimed/finished each section."""

    def __init__(self, addon: MaterialListsCog, record: dict[str, Any], page: int = 0) -> None:
        super().__init__(timeout=120)
        pages = addon.page_count(record)
        for label, delta in (('‹', -1), ('›', 1)):
            target = page + delta
            self.add_item(
                _EditorsNavButton(
                    addon,
                    record,
                    label,
                    target,
                    disabled=not (0 <= target < pages),
                )
            )


class TitleModal(discord.ui.Modal, title='Cambiar título del proyecto'):
    """Modal for editing a material list's title."""

    title_input: discord.ui.TextInput[TitleModal] = discord.ui.TextInput(label='Título', max_length=256)

    def __init__(self, addon: MaterialListsCog, record: dict[str, Any]) -> None:
        super().__init__()
        self.addon = addon
        self.record = record
        self.title_input.default = str(record['title'])

    async def on_submit(self, interaction: discord.Interaction) -> None:
        self.record['title'] = self.title_input.value.strip()
        await self.addon.store.save()
        await self.addon.refresh_record(self.record)
        await interaction.response.send_message('✅ Título actualizado.', ephemeral=True)


class MaterialListsCog(commands.Cog):
    """Slash command and reply-based section tracker for ``.litematic`` material lists."""

    def __init__(self, client: DisManagerClient) -> None:
        self.client = client
        self.store = Store()

    async def cog_load(self) -> None:
        for name in (
            'Check all materials',
            'Uncheck all materials',
            'Update all materials',
            'Material list editors',
            'Change material list title',
            'Delete material list',
        ):
            self.client.tree.remove_command(name, type=discord.AppCommandType.message)
        await self.restore_views()

    async def cog_unload(self) -> None:
        for name in (
            'Check all materials',
            'Uncheck all materials',
            'Update all materials',
            'Material list editors',
            'Change material list title',
            'Delete material list',
        ):
            self.client.tree.remove_command(name, type=discord.AppCommandType.message)

    @staticmethod
    def _is_admin(user: discord.abc.User) -> bool:
        return isinstance(user, discord.Member) and is_admin(user)

    def page_count(self, record: dict[str, Any]) -> int:
        return max(1, (len(record['items']) + 59) // 60)

    def embed(self, record: dict[str, Any]) -> discord.Embed:
        page = min(int(record.get('page', 0)), self.page_count(record) - 1)
        start = page * 60
        total_pages = self.page_count(record)
        title = f"> {record['title']}"
        if total_pages > 1:
            title += f' ({page + 1}/{total_pages})'
        embed = discord.Embed(title=title, colour=0x2B2D31)

        items = record['items']
        for column in range(3):
            section = items[start + column * 20 : start + (column + 1) * 20]
            values = [_format_section(item) for item in section]
            embed.add_field(name='', value='\n'.join(values) or '—', inline=True)

        embed.add_field(
            name='**Cómo interactuar:**',
            inline=False,
            value=(
                'Responde a este mensaje con uno de los comandos:\n'
                '• `claim <secciones>` : Reclamar secciones (📋)\n'
                '• `done <secciones>` : Marcar secciones completadas (✅)\n'
                '• `unclaim <secciones>` : Liberar secciones (❌)\n'
                '• `title <nuevo título>` : Cambiar el título de la lista\n'
                '\n'
                '*Ejemplo:* `claim A1 A2 A3`'
            ),
        )

        user = self.client.user
        if user is not None:
            author_text = (
                f"Autor esquema: {record.get('author', 'Desconocido')} | "
                f"Total bloques: {_format_blocks(int(record.get('total_blocks', 0)))}"
            )
            embed.set_footer(text=author_text, icon_url=user.display_avatar.url)
        return embed

    def editors_embed(self, record: dict[str, Any], page: int) -> discord.Embed:
        page = min(page, self.page_count(record) - 1)
        start = page * 60
        embed = discord.Embed(title=f"> {record['title']}", colour=0x2B2D31)
        items = record['items']
        for column in range(2):
            section = items[start + column * 30 : start + (column + 1) * 30]
            status = '\n'.join(str(item['status']) for item in section) or '—'
            section_names = '\n'.join(_short(str(item['section']), 18) for item in section) or '—'
            editors = '\n'.join(_short(str(item.get('edited_by') or '—'), 20) for item in section) or '—'
            names = ('✅', 'Sección', 'Constructor') if column == 0 else ('', '', '')
            embed.add_field(name=names[0], value=status, inline=True)
            embed.add_field(name=names[1], value=section_names, inline=True)
            embed.add_field(name=names[2], value=editors, inline=True)
        return embed

    async def refresh_record(self, record: dict[str, Any]) -> None:
        channel = self.client.get_channel(int(record['channel_id']))
        if not isinstance(channel, discord.abc.Messageable):
            return
        try:
            message = await channel.fetch_message(int(record['message_id']))
            await message.edit(embed=self.embed(record), view=ListView(self, str(record['id'])))
        except (discord.NotFound, discord.Forbidden):
            record['active'] = False
            await self.store.save()

    async def restore_views(self) -> None:
        for record in self.store.data.get('lists', {}).values():
            if not record.get('active'):
                continue
            channel_id = record.get('channel_id')
            if channel_id is None:
                continue
            channel = self.client.get_channel(int(channel_id))
            if not isinstance(channel, discord.abc.Messageable):
                continue
            try:
                await channel.fetch_message(int(record['message_id']))
            except (discord.NotFound, discord.Forbidden):
                record['active'] = False
                continue
            self.client.add_view(ListView(self, str(record['id'])), message_id=int(record['message_id']))
        await self.store.save()

    def find_record(self, message: discord.Message) -> dict[str, Any] | None:
        for record in self.store.data.get('lists', {}).values():
            if isinstance(record, dict) and record.get('active') and record.get('message_id') == message.id:
                return record
        return None

    @app_commands.command(
        name='material_list',
        description='Sube un archivo .litematic para generar secciones y materiales',
    )
    @app_commands.describe(attachment='Archivo .litematic del proyecto')
    async def material_list(
        self,
        interaction: discord.Interaction,
        attachment: discord.Attachment,
    ) -> None:
        if not self._is_admin(interaction.user):
            await interaction.response.send_message('No tienes permiso para crear listas.', ephemeral=True)
            return
        if not attachment.filename.lower().endswith('.litematic'):
            await interaction.response.send_message('Adjunta un archivo `.litematic` válido.', ephemeral=True)
            return
        if not isinstance(interaction.channel, discord.abc.Messageable):
            await interaction.response.send_message(
                'No se puede enviar mensajes en este canal.',
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)

        try:
            content = await attachment.read()
            parsed = parse_litematic(io.BytesIO(content))
        except Exception as error:
            await interaction.followup.send(
                f'Error procesando el archivo `.litematic`: {error}',
                ephemeral=True,
            )
            return

        filename_title = attachment.filename[: -len('.litematic')].strip()
        project_title = (filename_title or str(parsed.get('title') or 'Litematic Project'))[:256]
        record_id = uuid.uuid4().hex

        smp = self.client.find_process('SMP')
        if smp is not None:
            dest_dir = smp.path / 'server' / 'world' / 'data' / 'aeternum_materials'
            try:
                dest_dir.mkdir(parents=True, exist_ok=True)
                export_to_carpet_csv(parsed['materials'], dest_dir / f'{project_title}.csv')
                if smp.is_running():
                    smp.execute('materials reload')
            except Exception as error:
                print(f'[MaterialLists] Error al guardar CSV de materiales: {error}')

        items = [
            {
                'section': sec['section'],
                'blocks': sec['blocks'],
                'status': STATUS['unclaim'],
                'edited_by': 'Nadie',
                'dimensions': sec.get('dimensions', '—'),
            }
            for sec in parsed['sections']
        ]

        record: dict[str, Any] = {
            'id': record_id,
            'title': project_title,
            'author': parsed.get('author', 'Desconocido'),
            'total_blocks': parsed.get('total_blocks', 0),
            'items': items,
            'active': True,
            'page': 0,
            'message_id': None,
            'channel_id': interaction.channel_id,
        }

        message = await interaction.channel.send(embed=self.embed(record))
        record['message_id'] = message.id
        self.store.data['lists'][record_id] = record
        await message.edit(view=ListView(self, record_id))
        self.client.add_view(ListView(self, record_id), message_id=message.id)
        await self.store.save()
        await interaction.followup.send('✅ Lista creada.', ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot or not message.reference or not message.reference.message_id:
            return
        try:
            resolved = message.reference.resolved
            target = (
                resolved
                if isinstance(resolved, discord.Message)
                else await message.channel.fetch_message(message.reference.message_id)
            )
        except (discord.NotFound, discord.Forbidden):
            return
        record = self.find_record(target)
        if not record:
            return
        parts = message.content.strip().split()
        if not parts:
            return
        command = parts[0].lower()
        if command == 'title':
            if self._is_admin(message.author) and len(parts) > 1:
                record['title'] = ' '.join(parts[1:])[:256]
                await self.store.save()
                await self.refresh_record(record)
            await message.delete()
            return
        if command == 'editors':
            if self._is_admin(message.author):
                await message.reply(embed=self.editors_embed(record, 0))
            await message.delete()
            return
        if command not in STATUS:
            return
        if len(parts) > 1 and parts[1].lower() == 'all':
            if self._is_admin(message.author):
                for item in record['items']:
                    item['status'], item['edited_by'] = STATUS[command], message.author.display_name
                await self.store.save()
                await self.refresh_record(record)
            await message.delete()
            return
        section_indices = {
            str(item['section']).casefold(): index
            for index, item in enumerate(record['items'])
        }
        changed = False
        for section_name in parts[1:]:
            index = section_indices.get(section_name.casefold())
            if index is not None:
                item = record['items'][index]
                item['status'], item['edited_by'] = STATUS[command], message.author.display_name
                changed = True
        if changed:
            await self.store.save()
            await self.refresh_record(record)
        await message.delete()

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message) -> None:
        record = self.find_record(message)
        if record:
            record['active'] = False
            await self.store.save()
