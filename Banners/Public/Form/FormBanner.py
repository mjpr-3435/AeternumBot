from __future__ import annotations

from datetime import datetime

import discord
from Classes.config import get_ae_config
from dismanager.classes import DisManagerClient


def form_banner_embed(client: DisManagerClient, lang: str = 'es') -> discord.Embed:
    """Build the application form instructions embed in ``es`` or ``en``."""
    if lang == 'en':
        banner = (
            discord.Embed(
                title='> Form',
                description=(
                    'Hello and welcome to the server form system! Below we explain how to apply:\n\n'
                    '`         Remember that the server is Premium.         `'
                ),
                colour=0x2F3136,
                timestamp=datetime.now(),
            )
            .add_field(
                name='> Answer the questions',
                value=(
                    'Press the `Complete Form` button below to fill in your details, choose the '
                    'roles you are interested in, and tell us about your experience.'
                ),
                inline=False,
            )
            .add_field(
                name='`Grinder`',
                value=(
                    'Survival player (gathering, mining, building, etc.).\n'
                    '[[Examples]](https://discord.com/channels/839325517529612348/1023464870777200640)'
                ),
                inline=True,
            )
            .add_field(
                name='`Builder`',
                value=(
                    'Designs decorations in creative.\n'
                    '[[Examples]](https://discord.com/channels/839325517529612348/1423053488900014091)'
                ),
                inline=True,
            )
            .add_field(
                name='`Redstoner`',
                value=(
                    'Designs mechanisms in creative.\n'
                    '[[Examples]](https://discord.com/channels/839325517529612348/1233679850447835167)'
                ),
                inline=True,
            )
            .add_field(
                name='> Send evidence',
                value=(
                    'Inside the form itself you must attach images of your projects or your '
                    'Minecraft world matching the roles you chose (if you need to send videos or '
                    'extra screenshots afterwards, you can leave them in this channel).\n\n'
                    '`       We do not accept forms without evidence.       `'
                ),
                inline=False,
            )
            .add_field(
                name='> Wait for the vote',
                value=(
                    'After that your application will be submitted to voting and you should '
                    'receive an answer within an estimated 72 hours. Good luck!\n'
                    '↳ Any question you have can be left in this channel.\n'
                    '↳ If you want to cancel your application, close the ticket.'
                ),
                inline=False,
            )
        )
    else:
        banner = (
            discord.Embed(
                title='> Formulario',
                description=(
                    '¡Hola y bienvenido al sistema de formularios del servidor! '
                    'A continuación te explicaremos cómo postularte:\n\n'
                    '`         Recuerda que el servidor es Premium.         `'
                ),
                colour=0x2F3136,
                timestamp=datetime.now(),
            )
            .add_field(
                name='> Responde las preguntas',
                value=(
                    'Presiona el botón `Completar formulario` de abajo para rellenar tus datos, '
                    'elegir los roles que te interesan y contarnos sobre tu experiencia.'
                ),
                inline=False,
            )
            .add_field(
                name='`Grinder`',
                value=(
                    'Jugador de survival (recolección, minar, construir, etc.).\n'
                    '[[Ejemplos]](https://discord.com/channels/839325517529612348/1023464870777200640)'
                ),
                inline=True,
            )
            .add_field(
                name='`Builder`',
                value=(
                    'Diseña decoraciones en creativo.\n'
                    '[[Ejemplos]](https://discord.com/channels/839325517529612348/1423053488900014091)'
                ),
                inline=True,
            )
            .add_field(
                name='`Redstoner`',
                value=(
                    'Diseña mecanismos en creativo.\n'
                    '[[Ejemplos]](https://discord.com/channels/839325517529612348/1233679850447835167)'
                ),
                inline=True,
            )
            .add_field(
                name='> Mandar evidencia',
                value=(
                    'Dentro del mismo formulario deberás adjuntar imágenes de tus proyectos o de tu '
                    'mundo de Minecraft acordes a los roles escogidos (si necesitas enviar videos o '
                    'más capturas después, puedes dejarlas por este canal).\n\n'
                    '`       No aceptamos formularios sin evidencias.       `'
                ),
                inline=False,
            )
            .add_field(
                name='> Esperar la votación',
                value=(
                    'Hecho eso tu postulación será sometida a votación y se te dará respuesta en un '
                    'estimado máximo de 72 horas. ¡Buena suerte!\n'
                    '↳ Cualquier duda que tengas puedes dejarla por este canal.\n'
                    '↳ Si deseas cancelar tu postulación, cierra el ticket.'
                ),
                inline=False,
            )
        )

    icon_url = client.user.display_avatar.url if client.user is not None else None
    return banner.set_footer(text='Forms System \u200b', icon_url=icon_url).set_thumbnail(
        url=get_ae_config(client).thumbnail
    )
