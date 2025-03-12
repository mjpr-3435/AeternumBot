from ..Modules import *

def form_banner_embed(client: commands.Bot):
    banner = discord.Embed(
            title = f'> Formulario',
            colour = 0x2f3136,
            timestamp = datetime.now(),
            description = '¡Hola y bienvenido al sistema de formularios del servidor! A continuación te  explicaremos cómo postularte:')\
        .add_field(name = '> Responde las preguntas', inline = False, value = 
            'Como parte de tu postulación te pediremos que respondas las preguntas que se muestran en el desplegable de abajo. Las preguntas personales son obligatorias, las de rol te pedimos que escojas al menos uno.')\
        .add_field(name = '> Mandar evidencia', inline = False, value = 
            'Una vez hayas respondido las preguntas, usa este canal para enviar evidencias de que puedes desempeñar los roles que seleccionaste. Lo usual es mandar imágenes de tu mundo, pero si tienes otra cosa también es bienvenido.')\
        .add_field(name = '> Esperar la votación', inline = False, value = 
            'Hecho eso tu postulación será sometida a votación y se te dará respuesta en un estimado máximo de 72 horas. ¡Buena suerte!\n↳ Cualquier duda que tengas puedes dejarla por este canal.\n↳ Si deseas cancelar tu postulación, cierra el ticket.')\
        .set_footer(text = 'Forms System \u200b', icon_url = client.user.display_avatar)\
        .set_thumbnail(url = config_form['Thumbnail'])
    return banner