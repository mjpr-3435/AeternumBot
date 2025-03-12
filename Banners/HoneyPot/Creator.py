from .Modules import *

async def honey_creator(client: McDisClient) -> None:
    channel = client.get_channel(config['Channel ID'])

    try:
        messages = [msg async for msg in channel.history(oldest_first = True)]

        if len(messages) == 0:
            await channel.send(embed=banner_honeypot())

        elif len(messages) >= 1 and messages[0].author.id == client.user.id:
            await messages[0].edit(embed=banner_honeypot())
            
        else:
            await channel.purge()
            await honey_creator(client)

    except:
        print(f"Error:\n{traceback.format_exc()}")

def banner_honeypot() -> discord.Embed:
    embed = discord.Embed(
        title   = '> AETERNUM HONEYPOT',
        colour  = 0x2f3136)\
        .add_field      (inline = True, name = 'DONT SEND MESSAGE', value = 
            "Any message sent here will be considered a violation of server rules and will trigger an automatic ban without warning.\n\n\n"
            "This channel is intended solely for security purposes to protect our server from possible malicious activities, such as sending unwanted messages (spam) or abuse attempts.")\
        .add_field      (inline = True, name = 'NO ENVIAR MENSAJES', value = 
            "Cualquier mensaje enviado será considerado una violación a las reglas del servidor y obtendrás un baneo automático sin aviso.\n\n\n"
            "Este canal está destinado únicamente a fines de seguridad para proteger nuestro servidor de posibles actividades maliciosas, como el envío de mensajes no deseados (spam) o intentos de abuso.")\
        .set_image      (url = config['Honeypot PNG'])
    return embed

