from .Modules import *
import os

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


def twitch_embed() -> tuple[discord.Embed, list[discord.File]]:
    profiles_path = os.path.join(os.path.dirname(__file__), 'TwitchProfiles.png')
    thumb_path = os.path.join(os.path.dirname(__file__), 'TwitchBannerThumb.png')

    embed = discord.Embed(
        colour=0x6441A5,
        description=
            "> **Aeternum Twitch**\n"
            "https://www.twitch.tv/aeternumsmp\n\n"
            "> **Clave para stremear (poner en OBS)**\n"
            "||live_731189279_9YLQiLsakCJ6sRUTwRZOgrEWmZwyrL||\n\n"
            "> **Cinemática de Intro de Aeternum**\n"
            "https://drive.google.com/file/d/1ahOKFwtLJw5OiobmOkIV9Cv28GCwBWW9/view?usp=drive_link\n\n"
            "> **Overlay de la Música**\n"
            "https://6klabs.com/\n"
            "Sirve para YT Music (con el software Youtube Music Desktop App) y Spotify\n\n"
            "> **Página para generar tu imagen de este estilo**\n"
            "https://minecraftpfp.com/"
    )
    embed.set_image(url="attachment://TwitchProfiles.png")
    embed.set_thumbnail(url="attachment://TwitchBannerThumb.png")

    files = [
        discord.File(profiles_path, filename='TwitchProfiles.png'),
        discord.File(thumb_path, filename='TwitchBannerThumb.png'),
    ]
    return embed, files
