from ..Modules import *
from .LogInteraction import *

class form_banner_views(discord.ui.View):
    def __init__(self, owner_id):
        super().__init__(timeout = None)
        self.owner_id = owner_id

    @discord.ui.select( placeholder = 'Preguntas', 
                        options = [ discord.SelectOption(label = 'Personales'                   ,value = 0),
                                    discord.SelectOption(label = '(Rol) Grinder'                ,value = 1),
                                    discord.SelectOption(label = '(Rol) Redstoner'              ,value = 2),
                                    discord.SelectOption(label = '(Rol) Decorador'              ,value = 3)])
    async def role_form_selection(view, interaction: discord.Interaction, selection: discord.ui.Select):
        
        if interaction.user.id == view.owner_id:
            if   int(selection.values[0]) == 0:
                if form_info_request(interaction.message.id, ['log_message_id']):
                    await interaction.response.send_message('✖ Ya respondiste estas preguntas.', ephemeral = True, delete_after = 5)
                    return
                await interaction.response.send_modal(es_form_modal())
            elif int(selection.values[0]) == 1:
                if not form_info_request(interaction.message.id, ['log_message_id']):
                    await interaction.response.send_message('✖ Por favor, responde primero las preguntas personales.', ephemeral = True, delete_after = 5)
                    return
                await interaction.response.send_modal(es_form_grinder_modal())
            elif int(selection.values[0]) == 2:
                if not form_info_request(interaction.message.id, ['log_message_id']):
                    await interaction.response.send_message('✖ Por favor, responde primero las preguntas personales.', ephemeral = True, delete_after = 5)
                    return
                await interaction.response.send_modal(es_form_redstoner_modal())
            elif int(selection.values[0]) == 3:
                if not form_info_request(interaction.message.id, ['log_message_id']):
                    await interaction.response.send_message('✖ Por favor, responde primero las preguntas personales.', ephemeral = True, delete_after = 5)
                    return
                await interaction.response.send_modal(modal_form_builder())
        else:
            await interaction.response.send_message('✖ Solo puede interactuar con el formulario el creador del mismo.', ephemeral = True, delete_after = 5)


class modal_form_builder(discord.ui.Modal, title = 'Preguntas de Decorador'):
    question_1 = discord.ui.TextInput(label = 'Describe tu estilo de decoración', 
                                      style = discord.TextStyle.paragraph)
    question_2 = discord.ui.TextInput(label = 'Explica cómo planificas una decoración', 
                                      style = discord.TextStyle.paragraph)
    question_3 = discord.ui.TextInput(label = 'Cuéntanos cómo aprendiste a decorar', 
                                      style = discord.TextStyle.paragraph)
    question_4 = discord.ui.TextInput(label = '¿Utilizas WorldEdit? ¿Para qué exactamente?', 
                                      style = discord.TextStyle.paragraph)
    question_5 = discord.ui.TextInput(label = '¿Utilizas plugins de builders? ¿Cuáles?', 
                                      style = discord.TextStyle.paragraph)
                        
    async def on_submit(modal, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral = True, thinking = True)
        forms_channel = interaction.client.get_channel(config_form['Channel ID'])
        form = await forms_channel.fetch_message(form_info_request(interaction.message.id, ['log_message_id']))
        
        new_embed = form.embeds[0]\
            .add_field(inline = False, name = '> Preguntas de Builder' , value = '')\
            .add_field(inline = False, name = modal.question_1.label , value = str(modal.question_1).strip()[:1024])\
            .add_field(inline = False, name = modal.question_2.label , value = str(modal.question_2).strip()[:1024])\
            .add_field(inline = False, name = modal.question_3.label , value = str(modal.question_3).strip()[:1024])\
            .add_field(inline = False, name = modal.question_4.label , value = str(modal.question_4).strip()[:1024])\
            .add_field(inline = False, name = modal.question_5.label , value = str(modal.question_5).strip()[:1024])

        await form.edit(embeds = [new_embed])

        response = await interaction.followup.send('✔ Las respuestas fueron agregadas a tu formulario.\nNo olvides enviar tus evidencias!')
        await response.delete(delay = 60)


class es_form_grinder_modal(discord.ui.Modal, title = 'Preguntas de Grinder'):
    question_1 = discord.ui.TextInput(label = '¿Cuál es el rango de efecto de un beacon?')

    question_2 = discord.ui.TextInput(label = '¿Utilizas Litematica, MiniHud...? ¿Para qué?', 
                                      style = discord.TextStyle.paragraph)
    question_3 = discord.ui.TextInput(label = '¿Usas Item Shadowing? Explica cómo hacerlo', 
                                      style = discord.TextStyle.paragraph)
    question_4 = discord.ui.TextInput(label = 'Dinos distintas formas de hacer un perímetro', 
                                      style = discord.TextStyle.paragraph)
    question_5 = discord.ui.TextInput(label = '¿Cómo picas en un perímetro? Explícate', 
                                      style = discord.TextStyle.paragraph)
                        
    async def on_submit(modal, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral = True, thinking = True)
        forms_channel = interaction.client.get_channel(config_form['Channel ID'])
        form = await forms_channel.fetch_message(form_info_request(interaction.message.id, ['log_message_id']))
        
        new_embed = form.embeds[0]\
            .add_field(inline = False, name = '> Preguntas de Grinder' , value = '')\
            .add_field(inline = False, name = modal.question_1.label , value = str(modal.question_1).strip()[:1024])\
            .add_field(inline = False, name = modal.question_2.label , value = str(modal.question_2).strip()[:1024])\
            .add_field(inline = False, name = modal.question_3.label , value = str(modal.question_3).strip()[:1024])\
            .add_field(inline = False, name = modal.question_4.label , value = str(modal.question_4).strip()[:1024])\
            .add_field(inline = False, name = modal.question_5.label , value = str(modal.question_5).strip()[:1024])

        await form.edit(embeds = [new_embed])

        response = await interaction.followup.send('✔ Las respuestas fueron agregadas a tu formulario.\nNo olvides enviar tus evidencias!')
        await response.delete(delay = 60)

class es_form_redstoner_modal(discord.ui.Modal, title = 'Preguntas de Redstoner'):
    question_1 = discord.ui.TextInput(label = '¿Para qué se bloquean las tolvas?', 
                                      style = discord.TextStyle.paragraph)
    question_2 = discord.ui.TextInput(label = 'Explica la quasiconectividad', 
                                      style = discord.TextStyle.paragraph)
    question_3 = discord.ui.TextInput(label = 'Explica las funcionalidades de un Comparador', 
                                      style = discord.TextStyle.paragraph)
    question_4 = discord.ui.TextInput(label = '¿Qué es un cero tick?', 
                                      style = discord.TextStyle.paragraph)
    question_5 = discord.ui.TextInput(label = 'Menciona y explica las 5 fases del tick', 
                                      style = discord.TextStyle.paragraph)
                        
    async def on_submit(modal, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral = True, thinking = True)
        forms_channel = interaction.client.get_channel(config_form['Channel ID'])
        form = await forms_channel.fetch_message(form_info_request(interaction.message.id, ['log_message_id']))
        
        new_embed = form.embeds[0]\
            .add_field(inline = False, name = '> Preguntas de Redstoner' , value = '')\
            .add_field(inline = False, name = modal.question_1.label , value = str(modal.question_1).strip()[:1024])\
            .add_field(inline = False, name = modal.question_2.label , value = str(modal.question_2).strip()[:1024])\
            .add_field(inline = False, name = modal.question_3.label , value = str(modal.question_3).strip()[:1024])\
            .add_field(inline = False, name = modal.question_4.label , value = str(modal.question_4).strip()[:1024])\
            .add_field(inline = False, name = modal.question_5.label , value = str(modal.question_5).strip()[:1024])

        await form.edit(embeds = [new_embed])

        response = await interaction.followup.send('✔ Las respuestas fueron agregadas a tu formulario.\nNo olvides enviar tus evidencias!')
        await response.delete(delay = 60)

class es_form_modal(discord.ui.Modal, title = 'Formulario de ingreso'):
    question_1 = discord.ui.TextInput(label = 'Edad, país y nick de MC')
    question_2 = discord.ui.TextInput(label = '¿Por qué deseas aplicar a Aeternum?', 
                                      style = discord.TextStyle.paragraph)
    question_3 = discord.ui.TextInput(label = '¿Cuánto tiempo llevas jugando MC técnico?', 
                                      style = discord.TextStyle.paragraph)
    question_4 = discord.ui.TextInput(label = '¿Has estado en algún servidor técnico?', 
                                      style = discord.TextStyle.paragraph)
    question_5 = discord.ui.TextInput(label = '¿Qué crees que puedes aportar a Aeternum?', 
                                      style = discord.TextStyle.paragraph)
                        
    async def on_submit(modal, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral = True, thinking = True)
        form_embed = discord.Embed(
                colour = 0x2f3136, 
                timestamp = datetime.now())\
            .set_footer(text = 'Forms System \u200b', icon_url = interaction.client.user.display_avatar)\
            .add_field(inline = False, name = f'> Formulario {interaction.user.display_name}', value = '')\
            .add_field(inline = False, name = f'Cuenta de discord'   , value = interaction.user.mention)\
            .add_field(inline = False, name = modal.question_1.label , value = str(modal.question_1).strip()[:1024])\
            .add_field(inline = False, name = modal.question_2.label , value = str(modal.question_2).strip()[:1024])\
            .add_field(inline = False, name = modal.question_3.label , value = str(modal.question_3).strip()[:1024])\
            .add_field(inline = False, name = modal.question_4.label , value = str(modal.question_4).strip()[:1024])\
            .add_field(inline = False, name = modal.question_5.label , value = str(modal.question_5).strip()[:1024])\
            .set_thumbnail(url = interaction.user.display_avatar)
        
        forms_channel = interaction.client.get_channel(config_form['Channel ID'])
        new_form = await forms_channel.send(embed = form_embed)
        try:
            await new_form.add_reaction(config_form['Emoji Yes'])
        except:
            await new_form.add_reaction('✅')
        
        try:
            await new_form.add_reaction(config_form['Emoji No'])
        except:
            await new_form.add_reaction('❌')
        
        form_info_update(interaction.message.id, {'log_message_id': new_form.id})
        
        response = await interaction.followup.send(f'✔ Las respuestas fueron agregadas a tu formulario.')
        await response.delete(delay = 60)