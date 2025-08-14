from ..Modules import *

def ticket_banner_embed(user:discord.User, ticket_number:int) -> discord.Embed:
    embed = discord.Embed(
        title = f'> Ticket {ticket_number:04}',
        colour = 0x2f3136,
        description = 
        'Bienvenido al sistema de tickets del servidor.\n'
        '↳ Puedes dejar cualquier duda que tengas por este canal.\n'
        '↳ Si deseas el formulario de ingreso, reacciona con 📋.\n'
        '↳ Para cerrar el ticket, reacciona con 🔒.\n',
        timestamp = datetime.now())\
        .set_footer(text = '\u200b ', icon_url = user.display_avatar)
    
    return embed