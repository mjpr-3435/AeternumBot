from .Modules import *


async def honey_pot_es_embed(client: McDisClient) -> discord.Embed:
    channel = resolve_honeypot_channel(client)
    log_thread = await thread(config["Log Thread Name"], channel, public=True)

    return (
        discord.Embed(
            colour=config["Accent Color"],
            title="> ⚠️ **NO ENVIAR MENSAJES**",
            description=(
                "Si envías un mensaje aquí, serás baneado. "
                "Este canal se usa para detectar spam de bots o cuentas hackeadas."
            ),
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
            title="> ⚠️ **DO NOT SEND MESSAGES**",
            description=(
                "If you send a message here, you will be banned. "
                "This channel is used to detect spam bots or compromised accounts."
            ),
        )
        .add_field(name="", inline=True, value=f"<#{log_thread.id}>")
        .set_thumbnail(url=config["Thumbnail"])
    )
