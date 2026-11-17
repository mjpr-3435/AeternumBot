from __future__ import annotations

from datetime import datetime
from typing import Any, cast

import discord
from Classes.config import get_ae_config
from dismanager.classes import DisManagerClient

from .LogInteraction import form_info_request, form_info_update


def _missing_form_text(lang: str) -> str:
    return (
        '✖ This form is no longer registered.'
        if lang == 'en'
        else '✖ Este formulario ya no esta registrado.'
    )


def _append_answers_embed(
    base_embed: discord.Embed,
    section_name: str,
    questions: list[tuple[str, discord.ui.TextInput[Any]]],
) -> discord.Embed:
    new_embed = discord.Embed.from_dict(base_embed.to_dict())
    new_embed.add_field(inline=False, name=section_name, value='')
    for label_text, question in questions:
        new_embed.add_field(
            inline=False,
            name=label_text or 'Question',
            value=question.value.strip()[:1024] or '-',
        )
    return new_embed


async def _append_answers_to_logged_form(
    interaction: discord.Interaction,
    section_name: str,
    questions: list[tuple[str, discord.ui.TextInput[Any]]],
    success_text: str,
    lang: str,
) -> None:
    await interaction.response.defer(ephemeral=True, thinking=True)
    if interaction.message is None:
        return
    log_message_id = form_info_request(interaction.message.id, ['log_message_id'])
    if not log_message_id:
        response = await interaction.followup.send(_missing_form_text(lang), wait=True)
        await response.delete(delay=8)
        return

    client = cast(DisManagerClient, interaction.client)
    forms_channel = client.get_channel(get_ae_config(client).forms.channel_id)
    if not isinstance(forms_channel, discord.abc.Messageable):
        response = await interaction.followup.send(_missing_form_text(lang), wait=True)
        await response.delete(delay=8)
        return

    form_message = await forms_channel.fetch_message(int(log_message_id))
    updated_embed = _append_answers_embed(form_message.embeds[0], section_name, questions)
    await form_message.edit(embeds=[updated_embed])
    response = await interaction.followup.send(success_text, wait=True)
    await response.delete(delay=60)


async def _submit_personal_form(
    interaction: discord.Interaction,
    questions: list[tuple[str, discord.ui.TextInput[Any]]],
    *,
    lang: str,
) -> None:
    await interaction.response.defer(ephemeral=True, thinking=True)
    if interaction.message is None or interaction.channel is None:
        return

    client = cast(DisManagerClient, interaction.client)
    icon_url = client.user.display_avatar.url if client.user is not None else None
    title = f'> Form {interaction.user.display_name}' if lang == 'en' else f'> Formulario {interaction.user.display_name}'
    account_label = 'Discord account' if lang == 'en' else 'Cuenta de discord'
    ticket_mention = interaction.channel.mention if isinstance(interaction.channel, discord.TextChannel) else f'<#{interaction.channel_id}>'

    form_embed = (
        discord.Embed(colour=0x2F3136, timestamp=datetime.now())
        .set_footer(text='Forms System \u200b', icon_url=icon_url)
        .add_field(inline=False, name=title, value='')
        .add_field(inline=True, name=account_label, value=interaction.user.mention)
        .add_field(inline=True, name='Ticket', value=ticket_mention)
        .set_thumbnail(url=interaction.user.display_avatar.url)
    )
    for label_text, question in questions:
        form_embed.add_field(
            inline=False,
            name=label_text or 'Question',
            value=question.value.strip()[:1024] or '-',
        )

    forms_cfg = get_ae_config(client).forms
    forms_channel = client.get_channel(forms_cfg.channel_id)
    if not isinstance(forms_channel, discord.abc.Messageable):
        return

    new_form = await forms_channel.send(embed=form_embed)
    for custom_emoji, fallback in (
        (forms_cfg.emoji_yes, '✅'),
        (forms_cfg.emoji_no, '❌'),
    ):
        try:
            await new_form.add_reaction(custom_emoji)
        except discord.HTTPException:
            await new_form.add_reaction(fallback)

    form_info_update(interaction.message.id, {'log_message_id': new_form.id})
    updated_embed = discord.Embed.from_dict(interaction.message.embeds[0].to_dict())
    if lang == 'en':
        updated_embed.add_field(
            name='> Registered Form',
            value=f'📋{new_form.jump_url} (Utility for interviewers)',
        )
        ack = '✔ Answers added to your form.'
    else:
        updated_embed.add_field(
            name='> Formulario Registrado',
            value=f'📋{new_form.jump_url} (Utilidad para los entrevistadores)',
        )
        ack = '✔ Las respuestas fueron agregadas a tu formulario.'

    await interaction.message.edit(embed=updated_embed)
    response = await interaction.followup.send(ack, wait=True)
    await response.delete(delay=60)


class FormBannerView(discord.ui.View):
    """Persistent section selector view for application forms."""

    def __init__(self, owner_id: int, lang: str = 'es') -> None:
        super().__init__(timeout=None)
        self.owner_id = owner_id
        self.lang = lang

        for child in self.children:
            if isinstance(child, discord.ui.Select) and child.custom_id == 'form:section_select':
                if lang == 'en':
                    child.placeholder = 'Questions'
                    child.options = [
                        discord.SelectOption(label='Personal', value='0'),
                        discord.SelectOption(label='(Role) Grinder', value='1'),
                        discord.SelectOption(label='(Role) Redstoner', value='2'),
                        discord.SelectOption(label='(Role) Builder', value='3'),
                    ]
                else:
                    child.placeholder = 'Preguntas'
                    child.options = [
                        discord.SelectOption(label='Personales', value='0'),
                        discord.SelectOption(label='(Rol) Grinder', value='1'),
                        discord.SelectOption(label='(Rol) Redstoner', value='2'),
                        discord.SelectOption(label='(Rol) Decorador', value='3'),
                    ]

    @discord.ui.select(
        placeholder='Preguntas',
        row=0,
        custom_id='form:section_select',
        options=[
            discord.SelectOption(label='Personales', value='0'),
            discord.SelectOption(label='(Rol) Grinder', value='1'),
            discord.SelectOption(label='(Rol) Redstoner', value='2'),
            discord.SelectOption(label='(Rol) Decorador', value='3'),
        ],
    )
    async def role_form_selection(
        self,
        interaction: discord.Interaction,
        selection: discord.ui.Select[FormBannerView],
    ) -> None:
        if interaction.message is None:
            return
        log_message_id = form_info_request(interaction.message.id, ['log_message_id'])
        if log_message_id is None:
            await interaction.response.send_message(
                _missing_form_text(self.lang),
                ephemeral=True,
                delete_after=5,
            )
            return

        if interaction.user.id != self.owner_id:
            text = (
                '✖ Only the form creator can interact with it.'
                if self.lang == 'en'
                else '✖ Solo puede interactuar con el formulario su creador.'
            )
            await interaction.response.send_message(text, ephemeral=True, delete_after=5)
            return

        selected = int(selection.values[0])
        has_personal = bool(log_message_id)

        if selected == 0:
            if has_personal:
                text = (
                    '✖ You already answered these questions.'
                    if self.lang == 'en'
                    else '✖ Ya respondiste estas preguntas.'
                )
                await interaction.response.send_message(text, ephemeral=True, delete_after=5)
                return
            await interaction.response.send_modal(EnFormModal() if self.lang == 'en' else EsFormModal())
            return

        if not has_personal:
            text = (
                '✖ Please answer the personal questions first.'
                if self.lang == 'en'
                else '✖ Por favor, responde primero las preguntas personales.'
            )
            await interaction.response.send_message(text, ephemeral=True, delete_after=5)
            return

        modal_map: dict[int, discord.ui.Modal] = (
            {1: EnFormGrinderModal(), 2: EnFormRedstonerModal(), 3: EnFormBuilderModal()}
            if self.lang == 'en'
            else {1: EsFormGrinderModal(), 2: EsFormRedstonerModal(), 3: EsFormBuilderModal()}
        )
        modal = modal_map.get(selected)
        if modal is not None:
            await interaction.response.send_modal(modal)


class _FormQuestionsModal(discord.ui.Modal):
    def __init__(
        self,
        *,
        title: str,
        prompts: tuple[tuple[str, discord.TextStyle], ...],
    ) -> None:
        super().__init__(title=title)
        self.questions: list[tuple[str, discord.ui.TextInput[Any]]] = []
        for label_text, style in prompts:
            item: discord.ui.TextInput[Any] = discord.ui.TextInput(style=style)
            self.questions.append((label_text, item))
            self.add_item(discord.ui.Label(text=label_text, component=item))


class EsFormBuilderModal(_FormQuestionsModal):
    def __init__(self) -> None:
        super().__init__(
            title='Preguntas de Decorador',
            prompts=(
                ('Describe tu estilo de decoracion', discord.TextStyle.paragraph),
                ('Explica como planificas una decoracion', discord.TextStyle.paragraph),
                ('Cuentanos como aprendiste a decorar', discord.TextStyle.paragraph),
                ('Usas WorldEdit? Para que exactamente?', discord.TextStyle.paragraph),
                ('Usas plugins de builders? Cuales?', discord.TextStyle.paragraph),
            ),
        )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await _append_answers_to_logged_form(
            interaction,
            '> Preguntas de Builder',
            self.questions,
            '✔ Las respuestas fueron agregadas a tu formulario.\nNo olvides enviar tus evidencias.',
            'es',
        )


class EnFormBuilderModal(_FormQuestionsModal):
    def __init__(self) -> None:
        super().__init__(
            title='Builder Questions',
            prompts=(
                ('Describe your decoration style', discord.TextStyle.paragraph),
                ('Explain how you plan a decoration', discord.TextStyle.paragraph),
                ('Tell us how you learned decoration', discord.TextStyle.paragraph),
                ('Do you use WorldEdit? What for exactly?', discord.TextStyle.paragraph),
                ('Do you use builder plugins? Which ones?', discord.TextStyle.paragraph),
            ),
        )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await _append_answers_to_logged_form(
            interaction,
            '> Builder Questions',
            self.questions,
            '✔ Answers added to your form.\nDo not forget to send your evidence.',
            'en',
        )


class EsFormGrinderModal(_FormQuestionsModal):
    def __init__(self) -> None:
        super().__init__(
            title='Preguntas de Grinder',
            prompts=(
                ('Cual es el rango de efecto de un beacon?', discord.TextStyle.short),
                ('Utilizas Litematica, MiniHud...? Para que?', discord.TextStyle.paragraph),
                ('Usas Item Shadowing? Explica como hacerlo', discord.TextStyle.paragraph),
                ('Dinos distintas formas de hacer un perimetro', discord.TextStyle.paragraph),
                ('Como picas en un perimetro? Explicate', discord.TextStyle.paragraph),
            ),
        )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await _append_answers_to_logged_form(
            interaction,
            '> Preguntas de Grinder',
            self.questions,
            '✔ Las respuestas fueron agregadas a tu formulario.\nNo olvides enviar tus evidencias.',
            'es',
        )


class EnFormGrinderModal(_FormQuestionsModal):
    def __init__(self) -> None:
        super().__init__(
            title='Grinder Questions',
            prompts=(
                ('What is the effect range of a beacon?', discord.TextStyle.short),
                ('Do you use Litematica, MiniHud...? What for?', discord.TextStyle.paragraph),
                ('Do you use Item Shadowing? Explain it', discord.TextStyle.paragraph),
                ('Tell us different ways to make a perimeter', discord.TextStyle.paragraph),
                ('How do you mine in a perimeter? Explain it', discord.TextStyle.paragraph),
            ),
        )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await _append_answers_to_logged_form(
            interaction,
            '> Grinder Questions',
            self.questions,
            '✔ Answers added to your form.\nDo not forget to send your evidence.',
            'en',
        )


class EsFormRedstonerModal(_FormQuestionsModal):
    def __init__(self) -> None:
        super().__init__(
            title='Preguntas de Redstoner',
            prompts=(
                ('Para que se bloquean las tolvas?', discord.TextStyle.paragraph),
                ('Explica la quasiconectividad', discord.TextStyle.paragraph),
                ('Explica las funcionalidades de un comparador', discord.TextStyle.paragraph),
                ('Que es un cero tick?', discord.TextStyle.paragraph),
                ('Menciona y explica las 5 fases del tick', discord.TextStyle.paragraph),
            ),
        )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await _append_answers_to_logged_form(
            interaction,
            '> Preguntas de Redstoner',
            self.questions,
            '✔ Las respuestas fueron agregadas a tu formulario.\nNo olvides enviar tus evidencias.',
            'es',
        )


class EnFormRedstonerModal(_FormQuestionsModal):
    def __init__(self) -> None:
        super().__init__(
            title='Redstoner Questions',
            prompts=(
                ('What are locked hoppers used for?', discord.TextStyle.paragraph),
                ('Explain quasi-connectivity', discord.TextStyle.paragraph),
                ('Explain the functionality of a comparator', discord.TextStyle.paragraph),
                ('What is a zero tick?', discord.TextStyle.paragraph),
                ('Mention and explain the 5 phases of the tick', discord.TextStyle.paragraph),
            ),
        )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await _append_answers_to_logged_form(
            interaction,
            '> Redstoner Questions',
            self.questions,
            '✔ Answers added to your form.\nDo not forget to send your evidence.',
            'en',
        )


class EsFormModal(_FormQuestionsModal):
    def __init__(self) -> None:
        super().__init__(
            title='Formulario de ingreso',
            prompts=(
                ('Edad, pais y nick de MC', discord.TextStyle.short),
                ('Por que deseas aplicar a Aeternum?', discord.TextStyle.paragraph),
                ('Cuanto tiempo llevas jugando MC tecnico?', discord.TextStyle.paragraph),
                ('Has estado en algun servidor tecnico?', discord.TextStyle.paragraph),
                ('Que crees que puedes aportar a Aeternum?', discord.TextStyle.paragraph),
            ),
        )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await _submit_personal_form(
            interaction,
            self.questions,
            lang='es',
        )


class EnFormModal(_FormQuestionsModal):
    def __init__(self) -> None:
        super().__init__(
            title='Application Form',
            prompts=(
                ('Age, country and MC nickname', discord.TextStyle.short),
                ('Why do you want to apply to Aeternum?', discord.TextStyle.paragraph),
                ('How long have you been playing technical MC?', discord.TextStyle.paragraph),
                ('Have you been in any technical server?', discord.TextStyle.paragraph),
                ('How can you contribute to Aeternum?', discord.TextStyle.paragraph),
            ),
        )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await _submit_personal_form(
            interaction,
            self.questions,
            lang='en',
        )
