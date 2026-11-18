from __future__ import annotations

from datetime import datetime

import discord
from Classes.config import DiscordInfoConfig

_EMBED_COLOUR = 0x2F3136


def _active_duration_parts(foundation_date: str) -> tuple[int, int]:
    if not foundation_date.strip():
        return 0, 0
    days_total = (
        datetime.now().date()
        - datetime.strptime(foundation_date, '%Y-%m-%d').date()
    ).days
    return int(days_total // 365.25), int(days_total % 365.25)


def _format_links(links: tuple[str, ...], discord_invite: str, *, empty_text: str) -> str:
    rendered: list[str] = []
    for raw_entry in links:
        parts = [part.strip() for part in raw_entry.split(',', 2)]
        if len(parts) != 3:
            continue
        label, emoji, url = parts
        if not label or not url:
            continue
        if url == '{invite}':
            url = discord_invite
        prefix = f'{emoji} ' if emoji else ''
        rendered.append(f'{prefix}[{label}]({url})')
    return '\n'.join(rendered) if rendered else empty_text


def apply_en_embed() -> list[discord.Embed]:
    """Build the English application instructions embeds."""
    return [
        discord.Embed(
            title='Apply to the Server',
            colour=0xDDF2FD,
            description=(
                'Joining Aeternum means you will become part of our internal community and gain '
                'access to our map, which is why we would like to get to know you better before '
                'allowing you access.'
            ),
        ),
        discord.Embed(
            title='Form',
            colour=0x9BBEC8,
            description=(
                'To do this, we will ask you to fill out a form that you can access after creating '
                'a ticket using the `Tickets` button. Once you have submitted your form, you can '
                'use the ticket to answer the interviewers’ questions.\n\n'
                'Keep in mind that this is your first impression with us, and therefore it will '
                'weigh the most when deciding whether or not you are granted access to the server. '
                'We recommend that you take your time, answer carefully, elaborate as much as you '
                'can, and be honest when responding to the questions.\n\n'
                'It is important to note that you will not be able to join the server without '
                'having at least one voice conversation with us first. Therefore, having a '
                'microphone is mandatory in order to complete the process.\n\n'
                'We mainly look for people who are already somewhat familiar with the playstyle, '
                'although we do not require advanced knowledge unless you want to focus on '
                'redstone or building. What matters most to us is having a good time. Remember, '
                'this is not an exam.'
            ),
        ),
    ]


def apply_es_embed() -> list[discord.Embed]:
    """Build the Spanish application instructions embeds."""
    return [
        discord.Embed(
            title='Aplicar al servidor',
            colour=0xDDF2FD,
            description=(
                'Ingresar a Aeternum significa que pasarás a ser parte de nuestra comunidad interna '
                'y que tendrás acceso a nuestro mapa, es por ello que nos gustaría conocerte mejor '
                'antes de permitirte ingresar a los mismos.'
            ),
        ),
        discord.Embed(
            title='Formulario',
            colour=0x9BBEC8,
            description=(
                'Para ello, te pediremos que rellenes un formulario al cual podrás acceder luego '
                'de crear un ticket usando el botón `Tickets`. Una vez hayas enviado tu '
                'formulario, podrás usar el ticket para responder las preguntas de los '
                'entrevistadores.\n\n'
                'Ten en cuenta que esta es tu primera impresión hacia nosotros y, por tanto, es '
                'también la que pesará más al momento de decidir si te damos acceso o no al '
                'servidor. Te recomendamos que te tomes tu tiempo, que respondas con cuidado, que te '
                'explayes lo más que puedas y que seas sincero al responder las preguntas.\n\n'
                'Es importante señalar que no podrás ingresar al servidor sin antes tener al menos '
                'una conversación de voz con nosotros. Por lo tanto, es indispensable contar con '
                'micrófono para poder completar el proceso.\n\n'
                'Nosotros buscamos principalmente gente que ya conozca más o menos el estilo de '
                'juego, aunque no exigimos conocimientos avanzados salvo que quieras dedicarte a '
                'diseñar en redstone o decorar. Lo principal para nosotros es pasarla bien. '
                'Recuerda que esto no es un examen.'
            ),
        ),
    ]


def banner_en_embed(
    discord_invite: str,
    *,
    foundation_date: str,
    thumbnail: str,
    version: str = '',
    links: tuple[str, ...] = (),
    open_apply: bool = True,
) -> discord.Embed:
    """Build the English main DiscordInfo banner embed."""
    years, days = _active_duration_parts(foundation_date)
    if years == 0:
        active_days = f'{days} days'
    elif days == 0:
        active_days = f'{years} years'
    else:
        active_days = f'{years} years {days} days'
    foundation_label = (
        foundation_date.strip().replace('-', '/')
        if foundation_date.strip()
        else 'Unconfigured'
    )
    links_value = _format_links(links, discord_invite, empty_text='*No links configured*')
    join_value = 'Certainly! Press the `Apply` button and follow the instructions.'
    if not open_apply:
        join_value += '\n`   Applications are currently closed.   `'

    return (
        discord.Embed(
            title='AeternumSMP',
            colour=_EMBED_COLOUR,
            description=(
                'Aeternum is a technical/decorative Minecraft server where our main goal is to '
                'have a good time.'
            ),
        )
        .add_field(
            name='Can I join Aeternum?',
            inline=False,
            value=join_value,
        )
        .add_field(
            name='Do you use mods in Aeternum?',
            inline=False,
            value=(
                'We try to keep the game as close to vanilla as possible, however, we use carpet '
                'mod and some other optimization mods. If you want more information, press '
                '`Server Info`.'
            ),
        )
        .add_field(
            name='Discord Server Rules',
            inline=False,
            value=(
                "If it's your first time here, we invite you to press the `Rules` button and take "
                'a look at the server rules. We want all users to have a pleasant stay and avoid '
                'conflicts with each other.'
            ),
        )
        .add_field(
            name='Aeternum Links',
            inline=True,
            value=links_value,
        )
        .add_field(
            name='Information',
            inline=True,
            value=(
                f'Active Time: {active_days}\n'
                f'Foundation: {foundation_label}\n'
                f"Version: {version or 'Unconfigured'}\n"
                'Premium: Yes\n'
            ),
        )
        .set_thumbnail(url=thumbnail)
    )


def banner_es_embed(
    discord_invite: str,
    *,
    foundation_date: str,
    thumbnail: str,
    version: str = '',
    links: tuple[str, ...] = (),
    open_apply: bool = True,
) -> discord.Embed:
    """Build the Spanish main DiscordInfo banner embed."""
    years, days = _active_duration_parts(foundation_date)
    if years == 0:
        active_days = f'{days} días'
    elif days == 0:
        active_days = f'{years} años'
    else:
        active_days = f'{years} años {days} días'
    foundation_label = (
        foundation_date.strip().replace('-', '/')
        if foundation_date.strip()
        else 'Sin configurar'
    )
    links_value = _format_links(links, discord_invite, empty_text='*Sin links configurados*')
    join_value = '¡Claro! Presiona el botón `Apply` y sigue las indicaciones.'
    if not open_apply:
        join_value += '\n`   Actualmente no se admiten postulaciones.   `'

    return (
        discord.Embed(
            title='AeternumSMP',
            colour=_EMBED_COLOUR,
            description=(
                'Aeternum es un servidor de Minecraft técnico/decorativo donde principalmente '
                'búscamos pasarla bien.'
            ),
        )
        .add_field(
            name='¿Puedo entrar a Aeternum?',
            inline=False,
            value=join_value,
        )
        .add_field(
            name='¿Usan mods en Aeternum?',
            inline=False,
            value=(
                'Tratamos de mantener el juego lo más cercano al vanilla posible, sin embargo, '
                'usamos _carpet mod_ y otros mods de optimización. Si deseas más información '
                'presiona `Server Info`.'
            ),
        )
        .add_field(
            name='Reglas del servidor de Discord',
            inline=False,
            value=(
                'Si es tu primera vez por acá, te invitamos a que presiones el botón `Rules` y le '
                'des un vistazo a las reglas del servidor. Deseamos que todos los usuarios tengan '
                'una estadía agradable y evitar conflictos entre los mismos.'
            ),
        )
        .add_field(
            name='Links de Aeternum',
            inline=True,
            value=links_value,
        )
        .add_field(
            name='Información',
            inline=True,
            value=(
                f'Tiempo activo: {active_days}\n'
                f'Fundación: {foundation_label}\n'
                f"Versión: {version or 'Sin configurar'}\n"
                'Premium: Sí\n'
            ),
        )
        .set_thumbnail(url=thumbnail)
        .set_footer(text='English version available on `En` button.')
    )


def _format_bullet_paragraph(raw: str) -> str:
    lines = [line.strip() for line in raw.splitlines() if line.strip()]
    if not lines:
        return '*Sin configurar*'
    return '\n'.join(line if line.startswith('- ') else f'- {line}' for line in lines)


def hardware_info_embed(discord_cfg: DiscordInfoConfig) -> discord.Embed:
    """Build the server hardware, Carpet rules, and mods embed from config."""
    host_block = (
        f'```asciidoc\n{discord_cfg.host_info.strip()}```'
        if discord_cfg.host_info.strip()
        else '*Sin configurar*'
    )
    return (
        discord.Embed(title='Servidor de Aeternum', colour=_EMBED_COLOUR)
        .add_field(
            name='> Información sobre el host',
            inline=False,
            value=host_block,
        )
        .add_field(
            name='> Carpet Rules',
            inline=True,
            value=_format_bullet_paragraph(discord_cfg.carpet_rules),
        )
        .add_field(
            name='> Server Mods',
            inline=True,
            value=_format_bullet_paragraph(discord_cfg.server_mods),
        )
    )


def rules_en_embed() -> list[discord.Embed]:
    """Build the English Discord rules embeds."""
    return [
        discord.Embed(
            title='Discord Server Rules',
            colour=0xDDF2FD,
            description=(
                'We want everyone to have a pleasant stay on the server, so we have a set of '
                "rules that we hope you'll follow if you choose to remain here."
            ),
        ),
        discord.Embed(
            title='Voice Channels',
            colour=0x9BBEC8,
            description=(
                'Respect participants in the voice channels, avoid making unnecessary noise. It is '
                'recommended to steer clear of controversial topics such as politics or sports, in '
                'general, any subject that could generate disputes among participants.'
            ),
        ),
        discord.Embed(
            title='Text Channels',
            colour=0x427D9D,
            description=(
                'Respect participants in the text channels, avoid spamming, and refrain from '
                'sending sensitive content. Similarly, it is recommended to avoid controversial '
                'topics such as politics or sports, in general, any subject that could generate '
                'disputes among participants.'
            ),
        ),
        discord.Embed(
            title='Terms and Conditions',
            colour=0x164863,
            description=(
                "By participating in this server, you agree to the terms and conditions of Discord's "
                'service. You can find the terms and conditions on the following page '
                '[[Discord TOS]](https://discord.com/terms).'
            ),
        ).set_footer(text='Violating any of these rules may result in your banning from the server.'),
    ]


def rules_es_embed() -> list[discord.Embed]:
    """Build the Spanish Discord rules embeds."""
    return [
        discord.Embed(
            title='Reglas del servidor de Discord',
            colour=0xDDF2FD,
            description=(
                'Deseamos que todos tengan una agradable estadía en el servidor, para ello tenemos '
                'una serie de reglas que esperamos que cumplas si permaneces en el mismo.'
            ),
        ),
        discord.Embed(
            title='Canales de voz',
            colour=0x9BBEC8,
            description=(
                'Respetar a los participantes de los canales de voz, no hacer bulla '
                'innecesariamente. Se recomienda evitar temas polémicos como la política o el '
                'deporte, en general, cualquier tema que pueda generar controversias entre los '
                'participantes.'
            ),
        ),
        discord.Embed(
            title='Canales de texto',
            colour=0x427D9D,
            description=(
                'Respetar a los participantes de los canales de texto, no hacer spam, no mandar '
                'contenido sensible. De igual forma, se recomienta evitar los temas polémicos como '
                'la política o el deporte, en general, cualquier tema que pueda generar '
                'controversias entre los participantes.'
            ),
        ),
        discord.Embed(
            title='Terminos y condiciones',
            colour=0x164863,
            description=(
                'Al participar en este servidor, aceptas los términos y condiciones del servicio de '
                'Discord. Los términos y condiciones los puedes encontrar en la siguiente página '
                '[[Discord TOS]](https://discord.com/terms).'
            ),
        ).set_footer(text='Incumplir cualquiera de estas normas puede conllevar a tu baneo del servidor.'),
    ]
