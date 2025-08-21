from ..Modules import *

def form_banner_embed(client: commands.Bot) -> discord.Embed:
    banner = discord.Embed(
    title='> Formulario',
    description=(
            '¡Hola y bienvenido al sistema de formularios del servidor! A continuación te explicaremos cómo postularte:\n\n'
            '`         Recuerda que el servidor es Premium.         `'
        ),
    colour=0x2f3136,
    timestamp=datetime.now()
    ).add_field(
        name='> Responde las preguntas',
        value=(
            'Como parte de tu postulación te pediremos que respondas las preguntas que se muestran en el desplegable de abajo. '
            'Responde las preguntas personales primero, luego escoge al menos un rol y responde las preguntas asociadas al mismo.'
        ),
        inline=False
    ).add_field(
        name='`Grinder`',
        value='Jugador de survival (recolección, minar, construir, etc.).\n[[Ejemplos]](https://discord.com/channels/839325517529612348/1023464870777200640)',
        inline=True
    ).add_field(
        name='`Builder`',
        value='Diseña decoraciones en creativo.\n[[Ejemplos]](https://discord.com/channels/839325517529612348/846588514949922886)',
        inline=True
    ).add_field(
        name='`Redstoner`',
        value='Diseña mecanismos en creativo.\n[[Ejemplos]](https://discord.com/channels/839325517529612348/1233679850447835167)',
        inline=True
    ).add_field(
        name='> Mandar evidencia',
        value=(
            'Una vez hayas respondido las preguntas, usa este canal para mandar imágenes de tus proyectos o tu mundo de Minecraft, '
            'si tienes otro tipo contenido relacionado también es aceptado. Lo que mandes debe ser acorde a los roles escogidos.\n\n'
            '`       No aceptamos formularios sin evidencias.       `'
        ),
        inline=False
    ).add_field(
        name='> Esperar la votación',
        value=(
            'Hecho eso tu postulación será sometida a votación y se te dará respuesta en un estimado máximo de 72 horas. ¡Buena suerte!\n'
            '↳ Cualquier duda que tengas puedes dejarla por este canal.\n'
            '↳ Si deseas cancelar tu postulación, cierra el ticket.'
        ),
        inline=False
    ).set_footer(
        text='Forms System \u200b',
        icon_url=client.user.display_avatar
    ).set_thumbnail(url=config_form['Thumbnail'])
    return banner