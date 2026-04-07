from ..Modules import *


def form_banner_embed(client: commands.Bot, lang: str = 'es') -> discord.Embed:
    if lang == 'en':
        banner = discord.Embed(
            title='> Form',
            description=(
                'Hello and welcome to the server form system! Below we explain how to apply:\n\n'
                '`         Remember that the server is Premium.         `'
            ),
            colour=0x2f3136,
            timestamp=datetime.now()
        ).add_field(
            name='> Answer the questions',
            value=(
                'As part of your application we will ask you to answer the questions shown in the dropdown below. '
                'Answer the personal questions first, then choose at least one role and answer the related questions.'
            ),
            inline=False
        ).add_field(
            name='`Grinder`',
            value='Survival player (gathering, mining, building, etc.).\n[[Examples]](https://discord.com/channels/839325517529612348/1023464870777200640)',
            inline=True
        ).add_field(
            name='`Builder`',
            value='Designs decorations in creative.\n[[Examples]](https://discord.com/channels/839325517529612348/846588514949922886)',
            inline=True
        ).add_field(
            name='`Redstoner`',
            value='Designs mechanisms in creative.\n[[Examples]](https://discord.com/channels/839325517529612348/1233679850447835167)',
            inline=True
        ).add_field(
            name='> Send evidence',
            value=(
                'Once you have answered the questions, use this channel to send images of your projects or your Minecraft world; '
                'if you have other related content it is also accepted. What you send must match the roles you chose.\n\n'
                '`       We do not accept forms without evidence.       `'
            ),
            inline=False
        ).add_field(
            name='> Wait for the vote',
            value=(
                'After that your application will be submitted to voting and you should receive an answer within an estimated 72 hours. Good luck!\n'
                '↳ Any question you have can be left in this channel.\n'
                '↳ If you want to cancel your application, close the ticket.'
            ),
            inline=False
        )
    else:
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
        )

    banner.set_footer(
        text='Forms System \u200b',
        icon_url=client.user.display_avatar
    ).set_thumbnail(url=config_form['Thumbnail'])
    return banner
