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
    questions: list[discord.ui.TextInput[Any]],
) -> discord.Embed:
    new_embed = discord.Embed.from_dict(base_embed.to_dict())
    new_embed.add_field(inline=False, name=section_name, value='')
    for question in questions:
        new_embed.add_field(
            inline=False,
            name=question.label or 'Question',
            value=question.value.strip()[:1024] or '-',
        )
    return new_embed


async def _append_answers_to_logged_form(
    interaction: discord.Interaction,
    section_name: str,
    questions: list[discord.ui.TextInput[Any]],
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
    forms_channel = client.get_channel(get_ae_config(client).discord_info.forms_channel_id)
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
    questions: list[discord.ui.TextInput[Any]],
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
    for question in questions:
        form_embed.add_field(
            inline=False,
            name=question.label or 'Question',
            value=question.value.strip()[:1024] or '-',
        )

    discord_cfg = get_ae_config(client).discord_info
    forms_channel = client.get_channel(discord_cfg.forms_channel_id)
    if not isinstance(forms_channel, discord.abc.Messageable):
        return

    new_form = await forms_channel.send(embed=form_embed)
    for custom_emoji, fallback in (
        (discord_cfg.form_emoji_yes, '✅'),
        (discord_cfg.form_emoji_no, '❌'),
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


class EsFormBuilderModal(discord.ui.Modal, title='Preguntas de Decorador'):
    question_1: discord.ui.TextInput[EsFormBuilderModal] = discord.ui.TextInput(
        label='Describe tu estilo de decoracion', style=discord.TextStyle.paragraph
    )
    question_2: discord.ui.TextInput[EsFormBuilderModal] = discord.ui.TextInput(
        label='Explica como planificas una decoracion', style=discord.TextStyle.paragraph
    )
    question_3: discord.ui.TextInput[EsFormBuilderModal] = discord.ui.TextInput(
        label='Cuentanos como aprendiste a decorar', style=discord.TextStyle.paragraph
    )
    question_4: discord.ui.TextInput[EsFormBuilderModal] = discord.ui.TextInput(
        label='Usas WorldEdit? Para que exactamente?', style=discord.TextStyle.paragraph
    )
    question_5: discord.ui.TextInput[EsFormBuilderModal] = discord.ui.TextInput(
        label='Usas plugins de builders? Cuales?', style=discord.TextStyle.paragraph
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await _append_answers_to_logged_form(
            interaction,
            '> Preguntas de Builder',
            [self.question_1, self.question_2, self.question_3, self.question_4, self.question_5],
            '✔ Las respuestas fueron agregadas a tu formulario.\nNo olvides enviar tus evidencias.',
            'es',
        )


class EnFormBuilderModal(discord.ui.Modal, title='Builder Questions'):
    question_1: discord.ui.TextInput[EnFormBuilderModal] = discord.ui.TextInput(
        label='Describe your decoration style', style=discord.TextStyle.paragraph
    )
    question_2: discord.ui.TextInput[EnFormBuilderModal] = discord.ui.TextInput(
        label='Explain how you plan a decoration', style=discord.TextStyle.paragraph
    )
    question_3: discord.ui.TextInput[EnFormBuilderModal] = discord.ui.TextInput(
        label='Tell us how you learned decoration', style=discord.TextStyle.paragraph
    )
    question_4: discord.ui.TextInput[EnFormBuilderModal] = discord.ui.TextInput(
        label='Do you use WorldEdit? What for exactly?', style=discord.TextStyle.paragraph
    )
    question_5: discord.ui.TextInput[EnFormBuilderModal] = discord.ui.TextInput(
        label='Do you use builder plugins? Which ones?', style=discord.TextStyle.paragraph
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await _append_answers_to_logged_form(
            interaction,
            '> Builder Questions',
            [self.question_1, self.question_2, self.question_3, self.question_4, self.question_5],
            '✔ Answers added to your form.\nDo not forget to send your evidence.',
            'en',
        )


class EsFormGrinderModal(discord.ui.Modal, title='Preguntas de Grinder'):
    question_1: discord.ui.TextInput[EsFormGrinderModal] = discord.ui.TextInput(
        label='Cual es el rango de efecto de un beacon?'
    )
    question_2: discord.ui.TextInput[EsFormGrinderModal] = discord.ui.TextInput(
        label='Utilizas Litematica, MiniHud...? Para que?', style=discord.TextStyle.paragraph
    )
    question_3: discord.ui.TextInput[EsFormGrinderModal] = discord.ui.TextInput(
        label='Usas Item Shadowing? Explica como hacerlo', style=discord.TextStyle.paragraph
    )
    question_4: discord.ui.TextInput[EsFormGrinderModal] = discord.ui.TextInput(
        label='Dinos distintas formas de hacer un perimetro', style=discord.TextStyle.paragraph
    )
    question_5: discord.ui.TextInput[EsFormGrinderModal] = discord.ui.TextInput(
        label='Como picas en un perimetro? Explicate', style=discord.TextStyle.paragraph
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await _append_answers_to_logged_form(
            interaction,
            '> Preguntas de Grinder',
            [self.question_1, self.question_2, self.question_3, self.question_4, self.question_5],
            '✔ Las respuestas fueron agregadas a tu formulario.\nNo olvides enviar tus evidencias.',
            'es',
        )


class EnFormGrinderModal(discord.ui.Modal, title='Grinder Questions'):
    question_1: discord.ui.TextInput[EnFormGrinderModal] = discord.ui.TextInput(
        label='What is the effect range of a beacon?'
    )
    question_2: discord.ui.TextInput[EnFormGrinderModal] = discord.ui.TextInput(
        label='Do you use Litematica, MiniHud...? What for?', style=discord.TextStyle.paragraph
    )
    question_3: discord.ui.TextInput[EnFormGrinderModal] = discord.ui.TextInput(
        label='Do you use Item Shadowing? Explain it', style=discord.TextStyle.paragraph
    )
    question_4: discord.ui.TextInput[EnFormGrinderModal] = discord.ui.TextInput(
        label='Tell us different ways to make a perimeter', style=discord.TextStyle.paragraph
    )
    question_5: discord.ui.TextInput[EnFormGrinderModal] = discord.ui.TextInput(
        label='How do you mine in a perimeter? Explain it', style=discord.TextStyle.paragraph
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await _append_answers_to_logged_form(
            interaction,
            '> Grinder Questions',
            [self.question_1, self.question_2, self.question_3, self.question_4, self.question_5],
            '✔ Answers added to your form.\nDo not forget to send your evidence.',
            'en',
        )


class EsFormRedstonerModal(discord.ui.Modal, title='Preguntas de Redstoner'):
    question_1: discord.ui.TextInput[EsFormRedstonerModal] = discord.ui.TextInput(
        label='Para que se bloquean las tolvas?', style=discord.TextStyle.paragraph
    )
    question_2: discord.ui.TextInput[EsFormRedstonerModal] = discord.ui.TextInput(
        label='Explica la quasiconectividad', style=discord.TextStyle.paragraph
    )
    question_3: discord.ui.TextInput[EsFormRedstonerModal] = discord.ui.TextInput(
        label='Explica las funcionalidades de un comparador', style=discord.TextStyle.paragraph
    )
    question_4: discord.ui.TextInput[EsFormRedstonerModal] = discord.ui.TextInput(
        label='Que es un cero tick?', style=discord.TextStyle.paragraph
    )
    question_5: discord.ui.TextInput[EsFormRedstonerModal] = discord.ui.TextInput(
        label='Menciona y explica las 5 fases del tick', style=discord.TextStyle.paragraph
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await _append_answers_to_logged_form(
            interaction,
            '> Preguntas de Redstoner',
            [self.question_1, self.question_2, self.question_3, self.question_4, self.question_5],
            '✔ Las respuestas fueron agregadas a tu formulario.\nNo olvides enviar tus evidencias.',
            'es',
        )


class EnFormRedstonerModal(discord.ui.Modal, title='Redstoner Questions'):
    question_1: discord.ui.TextInput[EnFormRedstonerModal] = discord.ui.TextInput(
        label='What are locked hoppers used for?', style=discord.TextStyle.paragraph
    )
    question_2: discord.ui.TextInput[EnFormRedstonerModal] = discord.ui.TextInput(
        label='Explain quasi-connectivity', style=discord.TextStyle.paragraph
    )
    question_3: discord.ui.TextInput[EnFormRedstonerModal] = discord.ui.TextInput(
        label='Explain the functionality of a comparator', style=discord.TextStyle.paragraph
    )
    question_4: discord.ui.TextInput[EnFormRedstonerModal] = discord.ui.TextInput(
        label='What is a zero tick?', style=discord.TextStyle.paragraph
    )
    question_5: discord.ui.TextInput[EnFormRedstonerModal] = discord.ui.TextInput(
        label='Mention and explain the 5 phases of the tick', style=discord.TextStyle.paragraph
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await _append_answers_to_logged_form(
            interaction,
            '> Redstoner Questions',
            [self.question_1, self.question_2, self.question_3, self.question_4, self.question_5],
            '✔ Answers added to your form.\nDo not forget to send your evidence.',
            'en',
        )


class EsFormModal(discord.ui.Modal, title='Formulario de ingreso'):
    question_1: discord.ui.TextInput[EsFormModal] = discord.ui.TextInput(label='Edad, pais y nick de MC')
    question_2: discord.ui.TextInput[EsFormModal] = discord.ui.TextInput(
        label='Por que deseas aplicar a Aeternum?', style=discord.TextStyle.paragraph
    )
    question_3: discord.ui.TextInput[EsFormModal] = discord.ui.TextInput(
        label='Cuanto tiempo llevas jugando MC tecnico?', style=discord.TextStyle.paragraph
    )
    question_4: discord.ui.TextInput[EsFormModal] = discord.ui.TextInput(
        label='Has estado en algun servidor tecnico?', style=discord.TextStyle.paragraph
    )
    question_5: discord.ui.TextInput[EsFormModal] = discord.ui.TextInput(
        label='Que crees que puedes aportar a Aeternum?', style=discord.TextStyle.paragraph
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await _submit_personal_form(
            interaction,
            [self.question_1, self.question_2, self.question_3, self.question_4, self.question_5],
            lang='es',
        )


class EnFormModal(discord.ui.Modal, title='Application Form'):
    question_1: discord.ui.TextInput[EnFormModal] = discord.ui.TextInput(label='Age, country and MC nickname')
    question_2: discord.ui.TextInput[EnFormModal] = discord.ui.TextInput(
        label='Why do you want to apply to Aeternum?', style=discord.TextStyle.paragraph
    )
    question_3: discord.ui.TextInput[EnFormModal] = discord.ui.TextInput(
        label='How long have you been playing technical MC?', style=discord.TextStyle.paragraph
    )
    question_4: discord.ui.TextInput[EnFormModal] = discord.ui.TextInput(
        label='Have you been in any technical server?', style=discord.TextStyle.paragraph
    )
    question_5: discord.ui.TextInput[EnFormModal] = discord.ui.TextInput(
        label='How can you contribute to Aeternum?', style=discord.TextStyle.paragraph
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await _submit_personal_form(
            interaction,
            [self.question_1, self.question_2, self.question_3, self.question_4, self.question_5],
            lang='en',
        )
