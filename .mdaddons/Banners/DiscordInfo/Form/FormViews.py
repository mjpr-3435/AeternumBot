from ..Modules import *
from .LogInteraction import *
from .FormBanner import form_banner_embed


def _answers_embed(base_embed: discord.Embed, section_name: str, questions: list[discord.ui.TextInput]) -> discord.Embed:
    new_embed = base_embed.add_field(inline=False, name=section_name, value='')
    for question in questions:
        new_embed = new_embed.add_field(inline=False, name=question.label, value=str(question).strip()[:1024])
    return new_embed


async def _append_answers_to_logged_form(interaction: discord.Interaction, section_name: str, questions: list[discord.ui.TextInput], success_text: str):
    await interaction.response.defer(ephemeral=True, thinking=True)
    forms_channel = interaction.client.get_channel(config_form['Channel ID'])
    form = await forms_channel.fetch_message(form_info_request(interaction.message.id, ['log_message_id']))
    await form.edit(embeds=[_answers_embed(form.embeds[0], section_name, questions)])
    response = await interaction.followup.send(success_text)
    await response.delete(delay=60)


class form_banner_views(discord.ui.View):
    def __init__(self, owner_id, lang: str = 'es'):
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
        ]
    )
    async def role_form_selection(self, interaction: discord.Interaction, selection: discord.ui.Select):
        if interaction.user.id != self.owner_id:
            text = '✖ Only the form creator can interact with it.' if self.lang == 'en' else '✖ Solo puede interactuar con el formulario el creador del mismo.'
            await interaction.response.send_message(text, ephemeral=True, delete_after=5)
            return

        selected = int(selection.values[0])
        has_personal = bool(form_info_request(interaction.message.id, ['log_message_id']))

        if selected == 0:
            if has_personal:
                text = '✖ You already answered these questions.' if self.lang == 'en' else '✖ Ya respondiste estas preguntas.'
                await interaction.response.send_message(text, ephemeral=True, delete_after=5)
                return
            await interaction.response.send_modal(en_form_modal() if self.lang == 'en' else es_form_modal())
            return

        if not has_personal:
            text = '✖ Please answer the personal questions first.' if self.lang == 'en' else '✖ Por favor, responde primero las preguntas personales.'
            await interaction.response.send_message(text, ephemeral=True, delete_after=5)
            return

        if selected == 1:
            await interaction.response.send_modal(en_form_grinder_modal() if self.lang == 'en' else es_form_grinder_modal())
        elif selected == 2:
            await interaction.response.send_modal(en_form_redstoner_modal() if self.lang == 'en' else es_form_redstoner_modal())
        elif selected == 3:
            await interaction.response.send_modal(en_form_builder_modal() if self.lang == 'en' else es_form_builder_modal())


class es_form_builder_modal(discord.ui.Modal, title='Preguntas de Decorador'):
    question_1 = discord.ui.TextInput(label='Describe tu estilo de decoración', style=discord.TextStyle.paragraph)
    question_2 = discord.ui.TextInput(label='Explica cómo planificas una decoración', style=discord.TextStyle.paragraph)
    question_3 = discord.ui.TextInput(label='Cuéntanos cómo aprendiste a decorar', style=discord.TextStyle.paragraph)
    question_4 = discord.ui.TextInput(label='¿Utilizas WorldEdit? ¿Para qué exactamente?', style=discord.TextStyle.paragraph)
    question_5 = discord.ui.TextInput(label='¿Utilizas plugins de builders? ¿Cuáles?', style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        await _append_answers_to_logged_form(interaction, '> Preguntas de Builder', [self.question_1, self.question_2, self.question_3, self.question_4, self.question_5], '✔ Las respuestas fueron agregadas a tu formulario.\nNo olvides enviar tus evidencias!')


class en_form_builder_modal(discord.ui.Modal, title='Builder Questions'):
    question_1 = discord.ui.TextInput(label='Describe your decoration style', style=discord.TextStyle.paragraph)
    question_2 = discord.ui.TextInput(label='Explain how you plan a decoration', style=discord.TextStyle.paragraph)
    question_3 = discord.ui.TextInput(label='Tell us how you learned decoration', style=discord.TextStyle.paragraph)
    question_4 = discord.ui.TextInput(label='Do you use WorldEdit? What for exactly?', style=discord.TextStyle.paragraph)
    question_5 = discord.ui.TextInput(label='Do you use builder plugins? Which ones?', style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        await _append_answers_to_logged_form(interaction, '> Builder Questions', [self.question_1, self.question_2, self.question_3, self.question_4, self.question_5], '✔ Answers added to your form.\nDo not forget to send your evidence!')


class es_form_grinder_modal(discord.ui.Modal, title='Preguntas de Grinder'):
    question_1 = discord.ui.TextInput(label='¿Cuál es el rango de efecto de un beacon?')
    question_2 = discord.ui.TextInput(label='¿Utilizas Litematica, MiniHud...? ¿Para qué?', style=discord.TextStyle.paragraph)
    question_3 = discord.ui.TextInput(label='¿Usas Item Shadowing? Explica cómo hacerlo', style=discord.TextStyle.paragraph)
    question_4 = discord.ui.TextInput(label='Dinos distintas formas de hacer un perímetro', style=discord.TextStyle.paragraph)
    question_5 = discord.ui.TextInput(label='¿Cómo picas en un perímetro? Explícate', style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        await _append_answers_to_logged_form(interaction, '> Preguntas de Grinder', [self.question_1, self.question_2, self.question_3, self.question_4, self.question_5], '✔ Las respuestas fueron agregadas a tu formulario.\nNo olvides enviar tus evidencias!')


class en_form_grinder_modal(discord.ui.Modal, title='Grinder Questions'):
    question_1 = discord.ui.TextInput(label='What is the effect range of a beacon?')
    question_2 = discord.ui.TextInput(label='Do you use Litematica, MiniHud...? What for?', style=discord.TextStyle.paragraph)
    question_3 = discord.ui.TextInput(label='Do you use Item Shadowing? Explain how to do it', style=discord.TextStyle.paragraph)
    question_4 = discord.ui.TextInput(label='Tell us different ways to make a perimeter', style=discord.TextStyle.paragraph)
    question_5 = discord.ui.TextInput(label='How do you mine in a perimeter? Explain it', style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        await _append_answers_to_logged_form(interaction, '> Grinder Questions', [self.question_1, self.question_2, self.question_3, self.question_4, self.question_5], '✔ Answers added to your form.\nDo not forget to send your evidence!')


class es_form_redstoner_modal(discord.ui.Modal, title='Preguntas de Redstoner'):
    question_1 = discord.ui.TextInput(label='¿Para qué se bloquean las tolvas?', style=discord.TextStyle.paragraph)
    question_2 = discord.ui.TextInput(label='Explica la quasiconectividad', style=discord.TextStyle.paragraph)
    question_3 = discord.ui.TextInput(label='Explica las funcionalidades de un Comparador', style=discord.TextStyle.paragraph)
    question_4 = discord.ui.TextInput(label='¿Qué es un cero tick?', style=discord.TextStyle.paragraph)
    question_5 = discord.ui.TextInput(label='Menciona y explica las 5 fases del tick', style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        await _append_answers_to_logged_form(interaction, '> Preguntas de Redstoner', [self.question_1, self.question_2, self.question_3, self.question_4, self.question_5], '✔ Las respuestas fueron agregadas a tu formulario.\nNo olvides enviar tus evidencias!')


class en_form_redstoner_modal(discord.ui.Modal, title='Redstoner Questions'):
    question_1 = discord.ui.TextInput(label='What are locked hoppers used for?', style=discord.TextStyle.paragraph)
    question_2 = discord.ui.TextInput(label='Explain quasi-connectivity', style=discord.TextStyle.paragraph)
    question_3 = discord.ui.TextInput(label='Explain the functionality of a comparator', style=discord.TextStyle.paragraph)
    question_4 = discord.ui.TextInput(label='What is a zero tick?', style=discord.TextStyle.paragraph)
    question_5 = discord.ui.TextInput(label='Mention and explain the 5 phases of the tick', style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        await _append_answers_to_logged_form(interaction, '> Redstoner Questions', [self.question_1, self.question_2, self.question_3, self.question_4, self.question_5], '✔ Answers added to your form.\nDo not forget to send your evidence!')


class es_form_modal(discord.ui.Modal, title='Formulario de ingreso'):
    question_1 = discord.ui.TextInput(label='Edad, país y nick de MC')
    question_2 = discord.ui.TextInput(label='¿Por qué deseas aplicar a Aeternum?', style=discord.TextStyle.paragraph)
    question_3 = discord.ui.TextInput(label='¿Cuánto tiempo llevas jugando MC técnico?', style=discord.TextStyle.paragraph)
    question_4 = discord.ui.TextInput(label='¿Has estado en algún servidor técnico?', style=discord.TextStyle.paragraph)
    question_5 = discord.ui.TextInput(label='¿Qué crees que puedes aportar a Aeternum?', style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        form_embed = discord.Embed(colour=0x2f3136, timestamp=datetime.now())\
            .set_footer(text='Forms System \u200b', icon_url=interaction.client.user.display_avatar)\
            .add_field(inline=False, name=f'> Formulario {interaction.user.display_name}', value='')\
            .add_field(inline=True, name='Cuenta de discord', value=interaction.user.mention)\
            .add_field(inline=True, name='Ticket', value=interaction.channel.mention)\
            .add_field(inline=False, name=self.question_1.label, value=str(self.question_1).strip()[:1024])\
            .add_field(inline=False, name=self.question_2.label, value=str(self.question_2).strip()[:1024])\
            .add_field(inline=False, name=self.question_3.label, value=str(self.question_3).strip()[:1024])\
            .add_field(inline=False, name=self.question_4.label, value=str(self.question_4).strip()[:1024])\
            .add_field(inline=False, name=self.question_5.label, value=str(self.question_5).strip()[:1024])\
            .set_thumbnail(url=interaction.user.display_avatar)
        forms_channel = interaction.client.get_channel(config_form['Channel ID'])
        new_form = await forms_channel.send(embed=form_embed)
        try:
            await new_form.add_reaction(config_form['Emoji Yes'])
        except:
            await new_form.add_reaction('✅')
        try:
            await new_form.add_reaction(config_form['Emoji No'])
        except:
            await new_form.add_reaction('❌')
        form_info_update(interaction.message.id, {'log_message_id': new_form.id})
        await interaction.message.edit(embed=interaction.message.embeds[0].add_field(name='> Formulario Registrado', value=f'📋{new_form.jump_url} (Utilidad para los entrevistadores)'))
        response = await interaction.followup.send('✔ Las respuestas fueron agregadas a tu formulario.')
        await response.delete(delay=60)


class en_form_modal(discord.ui.Modal, title='Application Form'):
    question_1 = discord.ui.TextInput(label='Age, country and MC nickname')
    question_2 = discord.ui.TextInput(label='Why do you want to apply to Aeternum?', style=discord.TextStyle.paragraph)
    question_3 = discord.ui.TextInput(label='How long have you been playing technical MC?', style=discord.TextStyle.paragraph)
    question_4 = discord.ui.TextInput(label='Have you been in any technical server?', style=discord.TextStyle.paragraph)
    question_5 = discord.ui.TextInput(label='What do you think you can contribute to Aeternum?', style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        form_embed = discord.Embed(colour=0x2f3136, timestamp=datetime.now())\
            .set_footer(text='Forms System \u200b', icon_url=interaction.client.user.display_avatar)\
            .add_field(inline=False, name=f'> Form {interaction.user.display_name}', value='')\
            .add_field(inline=True, name='Discord account', value=interaction.user.mention)\
            .add_field(inline=True, name='Ticket', value=interaction.channel.mention)\
            .add_field(inline=False, name=self.question_1.label, value=str(self.question_1).strip()[:1024])\
            .add_field(inline=False, name=self.question_2.label, value=str(self.question_2).strip()[:1024])\
            .add_field(inline=False, name=self.question_3.label, value=str(self.question_3).strip()[:1024])\
            .add_field(inline=False, name=self.question_4.label, value=str(self.question_4).strip()[:1024])\
            .add_field(inline=False, name=self.question_5.label, value=str(self.question_5).strip()[:1024])\
            .set_thumbnail(url=interaction.user.display_avatar)
        forms_channel = interaction.client.get_channel(config_form['Channel ID'])
        new_form = await forms_channel.send(embed=form_embed)
        try:
            await new_form.add_reaction(config_form['Emoji Yes'])
        except:
            await new_form.add_reaction('✅')
        try:
            await new_form.add_reaction(config_form['Emoji No'])
        except:
            await new_form.add_reaction('❌')
        form_info_update(interaction.message.id, {'log_message_id': new_form.id})
        await interaction.message.edit(embed=interaction.message.embeds[0].add_field(name='> Registered Form', value=f'📋{new_form.jump_url} (Utility for interviewers)'))
        response = await interaction.followup.send('✔ Answers added to your form.')
        await response.delete(delay=60)
