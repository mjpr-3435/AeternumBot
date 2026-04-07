from .Modules import *


async def honey_pot_es_embed(client: McDisClient) -> discord.Embed:
    channel = resolve_honeypot_channel(client)
    log_thread = await thread(config["Log Thread Name"], channel, public=True)

    return (
        discord.Embed(
            colour=config["Accent Color"],
            title="> HoneyPot",
            description=(
                "⚠️ **NO ENVIAR MENSAJES**\n"
                "Si envías un mensaje aquí, serás considerado un bot y serás baneado."
            ),
        )
        .add_field(
            name="> Aviso De Seguridad",
            inline=False,
            value="Este canal está destinado únicamente a fines de seguridad para detectar spam, bots e intentos de abuso.",
        )
        .add_field(name="", inline=True, value=f"<#{log_thread.id}>")
        .set_thumbnail(url=config["Thumbnail"])
    )


async def honey_pot_en_embed(client: McDisClient) -> discord.Embed:
    channel = resolve_honeypot_channel(client)
    log_thread = await thread(config["Log Thread Name"], channel, public=True)

    return (
        discord.Embed(
            colour=config["Accent Color"],
            title="> HoneyPot",
            description=(
                "⚠️ **DO NOT SEND MESSAGES**\n"
                "If you send a message here, you will be treated as a bot and banned."
            ),
        )
        .add_field(
            name="> Security Notice",
            inline=False,
            value="This channel exists only for security purposes to detect spam bots and abuse attempts.",
        )
        .add_field(name="", inline=True, value=f"<#{log_thread.id}>")
        .set_thumbnail(url=config["Thumbnail"])
    )
