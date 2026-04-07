from ..Modules import *


def ticket_banner_embed(user: discord.User, ticket_number: int, lang: str = 'es') -> discord.Embed:
    if lang == 'en':
        embed = discord.Embed(
            title=f'> Ticket {ticket_number:04}',
            colour=0x2f3136,
            description=
            'Welcome to the server ticket system.\n'
            '↳ You can leave any question you have in this channel.\n'
            '↳ If you want the application form, use the `Apply` button.\n'
            '↳ To close the ticket, use the `Close` button.\n',
            timestamp=datetime.now()
        ).set_footer(text='\u200b ', icon_url=user.display_avatar)
    else:
        embed = discord.Embed(
            title=f'> Ticket {ticket_number:04}',
            colour=0x2f3136,
            description=
            'Bienvenido al sistema de tickets del servidor.\n'
            '↳ Puedes dejar cualquier duda que tengas por este canal.\n'
            '↳ Si deseas el formulario de ingreso, usa el botón `Formulario`.\n'
            '↳ Para cerrar el ticket, usa el botón `Cerrar`.\n',
            timestamp=datetime.now()
        ).set_footer(text='\u200b ', icon_url=user.display_avatar)

    return embed
