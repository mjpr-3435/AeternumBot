from .Modules import *

def apoyo_embed() -> list[discord.Embed]:
    embeds = [
        discord.Embed(
            title='Server Jobs',
            colour=0x2f3136
        ).add_field(
            name='> Sobre Aeternum',
            value=(
                "El servidor, más allá de ser un SMP de Minecraft donde todos jugamos y la pasamos bien, "
                "requiere esfuerzo extra para mantenerse y atraer gente nueva. Hacemos tours, cuidamos el orden en Discord, "
                "sacamos buenas fotos, armamos cinemáticas, streams, etc."
            ),
            inline=False
        ).add_field(
            name='> Participación',
            value=(
                "Aeternum no solo depende de jugar: requiere financiamiento, mantenimiento y apoyo. "
                "Si puedes aportar, colabora con lo que te guste: código, renders, showcases, videos, cinemáticas, logos, gifs, mejoras en Discord, administración del Patreon, etc.\n\n"
                "No pedimos conocimientos previos: se aprende en el camino. Solo necesitamos disposición y ganas de alcanzar el nivel actual."
            ),
            inline=False
        ).add_field(
            name='> Cómo apoyar',
            value=(
                "Puedes crear un ticket, comentarlo en voice o usar los canales del foro <#1228482462280056943> según tu área de interés. "
                "Todo suma, y queremos que seguir construyendo proyectos técnicos sea siempre divertido."
            ),
            inline=False
        ).set_footer(text="¡Gracias por querer aportar a Aeternum!").set_thumbnail(url = config['Thumbnail'])
        ]

    return embeds

def perimetros_embed() -> list[discord.Embed]:
    embeds = [
        discord.Embed(
            title = 'Protocolos para perímetros',
            colour = 0xDDF2FD,
            description = 
            f'- '
            f'- '
            f'- '
            f'- '
            ),
        discord.Embed(
            title ='',
            colour = 0x9BBEC8,
            description =
                f''
                f'')]

    return embeds

def proyectos_embed() -> list[discord.Embed]:
    embeds = [
        discord.Embed(
            title = 'Protocolos para proyectos',
            colour = 0xDDF2FD,
            description = 
            f'- '
            f'- '
            f'- '
            f'- '
            ),
        discord.Embed(
            title ='',
            colour = 0x9BBEC8,
            description =
                f''
                f'')]
    
    return embeds

def decoraciones_embed() -> list[discord.Embed]:
    embeds = [
        discord.Embed(
            title = 'Protocolos para decoraciones',
            colour = 0xDDF2FD,
            description = 
            f'- '
            f'- '
            f'- '
            f'- '
            ),
        discord.Embed(
            title ='',
            colour = 0x9BBEC8,
            description =
                f''
                f'')]
    
    return embeds
