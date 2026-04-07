from .Embeds import honey_pot_es_embed
from .Modules import *
from .Views import HoneyPotView


async def honey_pot_creator(client: McDisClient):
    try:
        channel = resolve_honeypot_channel(client)
        banner_message = await find_honeypot_banner_message(client)
        embed = await honey_pot_es_embed(client)

        if banner_message is None:
            await channel.send(embed=embed, view=HoneyPotView())

        else:
            await banner_message.edit(embed=embed, view=HoneyPotView())

    except asyncio.CancelledError:
        return

    except (aiohttp.ClientError, discord.HTTPException):
        await asyncio.sleep(1)
        await honey_pot_creator(client)

    except:
        print(f"Error:\n{traceback.format_exc()}")


async def honey_pot_extras(client: McDisClient):
    return
