from __future__ import annotations

from datetime import datetime

import discord


def ticket_banner_embed(
    user: discord.abc.User,
    ticket_number: int,
    lang: str = 'es',
) -> discord.Embed:
    """Build the welcome embed inside a ticket channel."""
    if lang == 'en':
        description = (
            'Welcome to the server ticket system.\n'
            '↳ You can leave any question you have in this channel.\n'
            '↳ If you want the application form, use the `Apply` button.\n'
            '↳ To close the ticket, use the `Close` button.\n'
        )
    else:
        description = (
            'Bienvenido al sistema de tickets del servidor.\n'
            '↳ Puedes dejar cualquier duda que tengas por este canal.\n'
            '↳ Si deseas el formulario de ingreso, usa el botón `Formulario`.\n'
            '↳ Para cerrar el ticket, usa el botón `Cerrar`.\n'
        )

    return discord.Embed(
        title=f'> Ticket {ticket_number:04}',
        colour=0x2F3136,
        description=description,
        timestamp=datetime.now(),
    ).set_footer(text='\u200b ', icon_url=user.display_avatar.url)
