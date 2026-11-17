from __future__ import annotations

import traceback
from typing import cast

import discord
from Classes.config import get_ae_config
from dismanager.classes import DisManagerClient
from Utils.discord_helpers import is_admin

SHOWCASE_MENU_ID = 'showcase:menu'


def thread_name(title: str) -> str:
    """Format the extra-images thread title for a Showcase post."""
    cleaned = title.strip() or 'Showcase'
    return f'{cleaned[:84]}: Imágenes Extra'


def default_post_text(title: str) -> str:
    """Format the default Showcase post body."""
    cleaned = title.strip() or 'Showcase'
    return f'> **{cleaned}:**'


async def _fetch_showcase_thread(
    client: DisManagerClient,
    message: discord.Message,
) -> discord.Thread | None:
    if message.thread is not None:
        return message.thread

    thread = client.get_channel(message.id)
    if isinstance(thread, discord.Thread):
        return thread

    try:
        fetched = await client.fetch_channel(message.id)
    except (discord.NotFound, discord.Forbidden, discord.HTTPException):
        return None
    return fetched if isinstance(fetched, discord.Thread) else None


async def ensure_showcase_post_menu(post_message: discord.Message) -> None:
    """Attach the persistent Showcase management menu to ``post_message``."""
    await post_message.edit(view=ShowcasePostMenuView())


async def ensure_showcase_controls(client: DisManagerClient) -> None:
    """Sync the Showcase management menu across existing posts in the Showcase channel."""
    channel = client.get_channel(get_ae_config(client).discord_info.showcase_id)
    if not isinstance(channel, discord.TextChannel):
        return

    async for message in channel.history(limit=None, oldest_first=True):
        try:
            await ensure_showcase_post_menu(message)
        except Exception:
            print(f'Showcase control sync error for message {message.id}:\n{traceback.format_exc()}')


async def load_showcase_controls(client: DisManagerClient) -> None:
    """Register the persistent Showcase menu view and sync existing posts."""
    if not client.__dict__.get('_showcase_post_menu_loaded', False):
        client.add_view(ShowcasePostMenuView())
        client.__dict__['_showcase_post_menu_loaded'] = True
    await ensure_showcase_controls(client)


class ModifyShowcaseTitleModal(discord.ui.Modal, title='Modificar titulo'):
    """Modal for editing a Showcase thread title."""

    title_input: discord.ui.TextInput[ModifyShowcaseTitleModal]

    def __init__(self, current_title: str, target_thread: discord.Thread) -> None:
        super().__init__()
        self.target_thread = target_thread
        self.title_input = discord.ui.TextInput(
            default=current_title,
            style=discord.TextStyle.short,
            max_length=100,
            required=True,
        )
        self.add_item(discord.ui.Label(text='Edita el titulo del post', component=self.title_input))

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await self.target_thread.edit(name=self.title_input.value)
        await interaction.response.send_message('Titulo actualizado.', ephemeral=True)


class ModifyShowcaseTextModal(discord.ui.Modal, title='Modificar contenido'):
    """Modal for editing a Showcase post body."""

    text_input: discord.ui.TextInput[ModifyShowcaseTextModal]

    def __init__(self, current_text: str, target_message: discord.Message) -> None:
        super().__init__()
        self.target_message = target_message
        self.text_input = discord.ui.TextInput(
            default=current_text,
            style=discord.TextStyle.paragraph,
            required=True,
        )
        self.add_item(discord.ui.Label(text='Edita el contenido del post', component=self.text_input))

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await self.target_message.edit(content=self.text_input.value, view=ShowcasePostMenuView())
        await interaction.response.send_message('Contenido actualizado.', ephemeral=True)


class ModifyShowcaseFilesModal(discord.ui.Modal):
    """Modal with native file upload for adding or replacing Showcase post attachments."""

    def __init__(
        self,
        target_message: discord.Message,
        *,
        replace: bool,
        max_files: int,
    ) -> None:
        super().__init__(title='Reemplazar archivos' if replace else 'Agregar archivos')
        self.target_message = target_message
        self.replace = replace
        self.upload: discord.ui.FileUpload[ModifyShowcaseFilesModal] = discord.ui.FileUpload(
            min_values=1,
            max_values=max_files,
            required=True,
        )
        self.add_item(
            discord.ui.Label(
                text='Selecciona los archivos del post',
                component=self.upload,
            )
        )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True, thinking=True)
        new_files = [await attachment.to_file() for attachment in self.upload.values]
        if self.replace:
            target_files = new_files
            done_msg = 'Archivos reemplazados.'
        else:
            existing = [await att.to_file() for att in self.target_message.attachments]
            target_files = existing + new_files
            done_msg = 'Archivos agregados.'

        await self.target_message.edit(attachments=target_files, view=ShowcasePostMenuView())
        await interaction.followup.send(done_msg, ephemeral=True)


class ShowcasePostMenu(discord.ui.Select['ShowcasePostMenuView']):
    """Admin-only select menu for managing a Showcase post."""

    def __init__(self) -> None:
        options = [
            discord.SelectOption(label='Cambiar titulo', value='title', description='Edita el nombre del hilo'),
            discord.SelectOption(label='Cambiar mensaje', value='message', description='Edita el texto del post'),
            discord.SelectOption(label='Agregar archivos', value='add_files', description='Suma archivos al post'),
            discord.SelectOption(
                label='Reemplazar archivos',
                value='replace_files',
                description='Reemplaza todos los archivos',
            ),
        ]
        super().__init__(
            placeholder='Administrar post',
            custom_id=SHOWCASE_MENU_ID,
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        if not isinstance(interaction.user, discord.Member) or not is_admin(interaction.user):
            await interaction.response.send_message('No tienes permisos.', ephemeral=True, delete_after=2)
            return

        post_message = interaction.message
        if post_message is None:
            await interaction.response.send_message('No pude encontrar el post.', ephemeral=True)
            return

        client = cast(DisManagerClient, interaction.client)
        thread = await _fetch_showcase_thread(client, post_message)
        if thread is None:
            await interaction.response.send_message('No pude encontrar el hilo del post.', ephemeral=True)
            return

        action = self.values[0]
        if action == 'title':
            await interaction.response.send_modal(
                ModifyShowcaseTitleModal(current_title=thread.name, target_thread=thread)
            )
            return
        if action == 'message':
            await interaction.response.send_modal(
                ModifyShowcaseTextModal(current_text=post_message.content, target_message=post_message)
            )
            return
        if action == 'add_files':
            remaining = 10 - len(post_message.attachments)
            if remaining <= 0:
                await interaction.response.send_message(
                    'Este post ya tiene el máximo de 10 archivos.',
                    ephemeral=True,
                )
                return
            await interaction.response.send_modal(
                ModifyShowcaseFilesModal(post_message, replace=False, max_files=remaining)
            )
            return
        if action == 'replace_files':
            await interaction.response.send_modal(
                ModifyShowcaseFilesModal(post_message, replace=True, max_files=10)
            )
            return

        await interaction.response.send_message('Accion no reconocida.', ephemeral=True)


class ShowcasePostMenuView(discord.ui.View):
    """Persistent view attached to Showcase posts."""

    def __init__(self) -> None:
        super().__init__(timeout=None)
        self.add_item(ShowcasePostMenu())
