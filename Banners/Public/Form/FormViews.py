from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from typing import cast

import discord
from Classes.config import get_ae_config
from dismanager.classes import DisManagerClient

from .LogInteraction import (
    form_info_request,
    get_completed_sections,
    mark_section_completed,
)


def _missing_form_text(lang: str) -> str:
    return (
        '✖ The form record was not found. Please open a new form.'
        if lang == 'en'
        else '✖ No se encontró el registro del formulario. Abre uno nuevo.'
    )


class ApplicationFormModal(discord.ui.Modal):
    """Unified Components v2 application modal with role selector and mandatory image upload."""

    def __init__(self, *, form_message: discord.Message, lang: str) -> None:
        is_en = lang == 'en'
        super().__init__(title='Application Form' if is_en else 'Formulario de ingreso')
        self.form_message = form_message
        self.lang = lang

        self.basic_input: discord.ui.TextInput[ApplicationFormModal] = discord.ui.TextInput(
            style=discord.TextStyle.short,
            placeholder=(
                'E.g.: Steve, 20 years old, Mexico'
                if is_en
                else 'Ej: Steve, 20 años, Perú'
            ),
            max_length=150,
            required=True,
        )
        role_options = (
            [
                discord.SelectOption(
                    label='Grinder / Survival',
                    value='Grinder',
                    description='Gathering, mining, building and survival projects.',
                ),
                discord.SelectOption(
                    label='Builder / Decorator',
                    value='Builder',
                    description='Designing decorations and aesthetics in creative/survival.',
                ),
                discord.SelectOption(
                    label='Redstoner',
                    value='Redstoner',
                    description='Designing technical mechanisms, farms and storage.',
                ),
            ]
            if is_en
            else [
                discord.SelectOption(
                    label='Grinder / Survival',
                    value='Grinder',
                    description='Recolección, minar, construir y apoyar en proyectos.',
                ),
                discord.SelectOption(
                    label='Decorador / Builder',
                    value='Decorador',
                    description='Diseñar decoraciones y estética en creativo/survival.',
                ),
                discord.SelectOption(
                    label='Redstoner',
                    value='Redstoner',
                    description='Diseñar mecanismos técnicos, granjas y almacenamiento.',
                ),
            ]
        )
        self.roles_select: discord.ui.Select[ApplicationFormModal] = discord.ui.Select(
            placeholder=(
                'Select one or more roles...'
                if is_en
                else 'Selecciona uno o más roles...'
            ),
            min_values=1,
            max_values=len(role_options),
            options=role_options,
            required=True,
        )
        self.experience_input: discord.ui.TextInput[ApplicationFormModal] = discord.ui.TextInput(
            style=discord.TextStyle.paragraph,
            placeholder=(
                'Tell us about your worlds/servers, or what you enjoy doing (mining, building, farms)...'
                if is_en
                else 'Cuéntanos de tus mundos/servidores, o qué disfrutas hacer (minar, decorar, granjas)...'
            ),
            max_length=1000,
            required=True,
        )
        self.autonomy_input: discord.ui.TextInput[ApplicationFormModal] = discord.ui.TextInput(
            style=discord.TextStyle.paragraph,
            placeholder=(
                'Mention which mods you use (Litematica, MiniHUD, etc.) and how you learn on your own.'
                if is_en
                else 'Menciona qué mods manejas (Litematica, MiniHUD, etc.) y cómo investigas por tu cuenta.'
            ),
            max_length=1000,
            required=True,
        )
        self.evidence_upload: discord.ui.FileUpload[ApplicationFormModal] = discord.ui.FileUpload(
            min_values=1,
            max_values=10,
            required=True,
        )

        self.add_item(
            discord.ui.Label(
                text='Basic Info' if is_en else 'Datos básicos',
                description=(
                    'Your exact Minecraft nickname, age and country.'
                    if is_en
                    else 'Tu nick exacto de Minecraft, tu edad y tu país.'
                ),
                component=self.basic_input,
            )
        )
        self.add_item(
            discord.ui.Label(
                text='Roles of Interest' if is_en else 'Roles de interés',
                description=(
                    'Choose the areas where you want to participate in the server.'
                    if is_en
                    else 'Elige en qué áreas te interesa participar dentro del servidor.'
                ),
                component=self.roles_select,
            )
        )
        self.add_item(
            discord.ui.Label(
                text='Experience & Playstyle' if is_en else 'Experiencia y qué te gusta hacer',
                description=(
                    'What do you usually do in MC? If new to tech, how would you like to help or learn?'
                    if is_en
                    else '¿Qué sueles hacer en MC? Si eres nuevo en técnico, ¿en qué te gustaría apoyar o aprender?'
                ),
                component=self.experience_input,
            )
        )
        self.add_item(
            discord.ui.Label(
                text='Tools & Autonomy' if is_en else 'Herramientas y autonomía',
                description=(
                    'What mods do you use on your own and how do you figure out things you do not know?'
                    if is_en
                    else '¿Qué mods usas por tu cuenta y cómo te las arreglas cuando no sabes hacer algo?'
                ),
                component=self.autonomy_input,
            )
        )
        self.add_item(
            discord.ui.Label(
                text='Screenshots & Evidence' if is_en else 'Fotos y evidencias',
                description=(
                    'Upload screenshots of your worlds, builds or projects (1 to 10 images).'
                    if is_en
                    else 'Sube capturas de tus mundos, construcciones o proyectos (1 a 10 imágenes).'
                ),
                component=self.evidence_upload,
            )
        )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        is_en = self.lang == 'en'
        uploaded = list(self.evidence_upload.values)
        for attachment in uploaded:
            if attachment.content_type is not None and not attachment.content_type.startswith('image/'):
                msg = (
                    '✖ All uploaded files must be images.'
                    if is_en
                    else '✖ Todos los archivos subidos deben ser imágenes.'
                )
                await interaction.response.send_message(msg, ephemeral=True)
                return

        await interaction.response.defer(ephemeral=True, thinking=True)
        if not isinstance(interaction.channel, discord.abc.Messageable):
            return

        client = cast(DisManagerClient, interaction.client)
        forms_cfg = get_ae_config(client).forms
        forms_channel = client.get_channel(forms_cfg.channel_id)
        if not isinstance(forms_channel, discord.abc.Messageable):
            err = (
                '✖ The Forms channel is not configured (`Forms.Channel ID` in `/config`).'
                if is_en
                else '✖ El canal de Forms no está configurado (`Forms.Channel ID` en `/config`).'
            )
            await interaction.followup.send(err, ephemeral=True)
            return

        forms_files = [await att.to_file() for att in uploaded]

        icon_url = client.user.display_avatar.url if client.user is not None else None
        title = (
            f'> Form {interaction.user.display_name}'
            if is_en
            else f'> Formulario {interaction.user.display_name}'
        )
        account_label = 'Discord account' if is_en else 'Cuenta de discord'
        roles_label = 'Roles' if is_en else 'Roles de interés'
        basic_label = 'Basic Info' if is_en else 'Datos básicos'
        exp_label = 'Experience & Playstyle' if is_en else 'Experiencia y qué te gusta hacer'
        auto_label = 'Tools & Autonomy' if is_en else 'Herramientas y autonomía'
        ticket_mention = (
            interaction.channel.mention
            if isinstance(interaction.channel, discord.TextChannel)
            else f'<#{interaction.channel_id}>'
        )

        form_embed = (
            discord.Embed(colour=0x2F3136, timestamp=datetime.now())
            .set_footer(text='Forms System \u200b', icon_url=icon_url)
            .add_field(inline=False, name=title, value='')
            .add_field(inline=True, name=account_label, value=interaction.user.mention)
            .add_field(inline=True, name='Ticket', value=ticket_mention)
            .add_field(inline=True, name=roles_label, value=', '.join(self.roles_select.values))
            .add_field(inline=False, name=basic_label, value=self.basic_input.value.strip()[:1024] or '-')
            .add_field(inline=False, name=exp_label, value=self.experience_input.value.strip()[:1024] or '-')
            .add_field(inline=False, name=auto_label, value=self.autonomy_input.value.strip()[:1024] or '-')
            .set_thumbnail(url=interaction.user.display_avatar.url)
        )

        new_form = await forms_channel.send(embed=form_embed, files=forms_files)
        for custom_emoji, fallback in (
            (forms_cfg.emoji_yes, '✅'),
            (forms_cfg.emoji_no, '❌'),
        ):
            try:
                if custom_emoji.strip():
                    await new_form.add_reaction(custom_emoji)
                else:
                    await new_form.add_reaction(fallback)
            except discord.HTTPException:
                await new_form.add_reaction(fallback)

        owner_id, stored_lang, completed = mark_section_completed(
            self.form_message.id,
            'personal',
            log_message_id=new_form.id,
        )
        updated_embed = discord.Embed.from_dict(self.form_message.embeds[0].to_dict())
        if is_en:
            updated_embed.add_field(
                name='> Registered Form',
                value=f'📋{new_form.jump_url} (Utility for interviewers)',
            )
            ack = '✔ Your form and evidence were submitted.'
        else:
            updated_embed.add_field(
                name='> Formulario Registrado',
                value=f'📋{new_form.jump_url} (Utilidad para los entrevistadores)',
            )
            ack = '✔ Tu formulario y evidencias fueron enviados.'

        new_view = FormBannerView(owner_id, lang=stored_lang, completed=completed)
        client.add_view(new_view, message_id=self.form_message.id)
        await self.form_message.edit(embed=updated_embed, view=new_view)
        response = await interaction.followup.send(ack, ephemeral=True, wait=True)
        await response.delete(delay=30)


class _OpenFormButton(discord.ui.Button['FormBannerView']):
    def __init__(self, *, label: str, disabled: bool) -> None:
        super().__init__(
            label=label,
            style=discord.ButtonStyle.secondary,
            custom_id='form:btn:personal',
            disabled=disabled,
            row=0,
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        assert self.view is not None
        await self.view.handle_open(interaction)


class FormBannerView(discord.ui.View):
    """Persistent single-button view for opening the unified application form modal."""

    def __init__(
        self,
        owner_id: int,
        lang: str = 'es',
        completed: Iterable[str] = (),
    ) -> None:
        super().__init__(timeout=None)
        self.owner_id = owner_id
        self.lang = lang
        self.completed = set(completed)

        label = 'Complete Form' if lang == 'en' else 'Completar formulario'
        self.add_item(
            _OpenFormButton(
                label=label,
                disabled='personal' in self.completed,
            )
        )

    async def handle_open(self, interaction: discord.Interaction) -> None:
        if interaction.message is None:
            return
        log_message_id, owner_id = form_info_request(
            interaction.message.id,
            ['log_message_id', 'owner_id'],
        )
        if log_message_id is None:
            await interaction.response.send_message(
                _missing_form_text(self.lang),
                ephemeral=True,
                delete_after=5,
            )
            return

        effective_owner = int(owner_id) if owner_id else self.owner_id
        if interaction.user.id != effective_owner:
            text = (
                '✖ Only the form creator can interact with it.'
                if self.lang == 'en'
                else '✖ Solo puede interactuar con el formulario su creador.'
            )
            await interaction.response.send_message(text, ephemeral=True, delete_after=5)
            return

        completed = get_completed_sections(interaction.message.id)
        if 'personal' in completed or bool(log_message_id):
            text = (
                '✖ You already submitted your form.'
                if self.lang == 'en'
                else '✖ Ya enviaste tu formulario.'
            )
            await interaction.response.send_message(text, ephemeral=True, delete_after=5)
            return

        await interaction.response.send_modal(
            ApplicationFormModal(form_message=interaction.message, lang=self.lang)
        )
