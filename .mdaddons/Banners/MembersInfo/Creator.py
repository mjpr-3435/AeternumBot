from .TaskLog import show_tasks
from .Views import banner_views,update_whitelist_on_servers
from .Modules import *

async def members_creator(client: McDisClient, loop: bool = True):
    channel = client.get_channel(config['Channel ID'])
    update_whitelist_on_servers(client)

    while True:
        try:
            messages        = [msg async for msg in channel.history(limit = None, oldest_first = True)]
            banner_image    = discord.File(os.path.join(os.path.dirname(__file__), 'Banner.png'))
            banner          = await banner_embed(client)

            if len(messages) == 0:
                await channel.send(embed = banner, file = banner_image, view = banner_views())
            
            elif len(messages) == 1 and messages[0].author.id == client.user.id:
                await messages[0].edit(embed = banner, view = banner_views())
            
            else:
                await channel.purge(limit = 100)
                continue

            if not loop: break

        except asyncio.CancelledError:
            return
        
        except (aiohttp.ClientError, discord.HTTPException):
            channel = client.get_channel(config['Channel ID'])
            await asyncio.sleep(1)
            continue

        except:
            print(f'Error:\n{traceback.format_exc()}')

        else:
            await asyncio.sleep(24*60*60)

async def members_extras(client: McDisClient):
    from .TaskLog import update_log
    await update_log(client)

    extensions = ["Banners.MembersInfo.TaskCommand",
                  "Banners.MembersInfo.TaskBehaviour"]
    
    for extension in extensions:
        if extension in client.extensions:
            await client.unload_extension(extension)
    
        await client.load_extension(extension)

    await client.tree.sync()

async def banner_embed(client: McDisClient) -> discord.Embed:
    years = int(((datetime.today()-datetime.strptime(config['Foundation Date'], "%Y-%m-%d")).days)//365.25)
    days = int((datetime.today()-datetime.strptime(config['Foundation Date'], "%Y-%m-%d")).days%365.25)
    channel         = client.get_channel(config['Channel ID'])
    announcements   = await thread('Announcements', channel)
    whitelist_log   = await thread('Whitelist Log', channel, public = True)
    server_log      = await thread('Server Log', channel, public = True)
             
    if years == 0:
        active_days = f'Tiempo activo: {days} días'
    elif days == 0:
        active_days = f'Tiempo activo: {years} años'
    else:
        active_days = f'Tiempo activo: {years} años {days} días'
        
    embed = discord.Embed(colour = 0x2f3136)\
        .add_field(name = '> Información del servidor', inline = False, value =
            f'||```prolog\n'
            f'Ip:                                         '[:-len(config['IP Server'])] + config['IP Server'] + '\n'
            f'Ip Plugins:                                 '[:-len(config['IP Plugins'])] + config['IP Plugins'] + '\n'
            f'Ip Dummy:                                   '[:-len(config['IP Dummy'])] + config['IP Dummy'] + '\n'
            f'Seed:                                       '[:-len(config['Seed'])] + config['Seed'] + '```||\n')\
        .add_field(name = '', inline = True, value = f'<#{announcements.id}>')\
        .add_field(name = '', inline = True, value = f'<#{whitelist_log.id}>')\
        .add_field(name = '', inline = True, value = f'<#{server_log.id}>'   )\
        .add_field(name = '', inline = True, value = 'Fundación: 12-05-2021')\
        .add_field(name = '', inline = True, value = active_days)\
        .add_field(name = '> Donaciones' if False else '' ,inline = False, value = 
            # f'*El servidor siempre ha sido y seguirá siendo gratuito. Sin embargo, mantenerlo requiere dinero, y todos jugamos aquí.*\n'
            f'`    💸 Donaciones: {config["Link Paypal"]}    `')\
        .add_field(name = '> Reglas para miembros', inline = False, value =
        '- No filtrar mensajes fuera del servidor.\n'
        '- No se tolerará ningún tipo de toxicidad.\n'
        '- Quien grifee el servidor será baneado permanente.\n'
        '- Si se llegara a romper una granja, AVISA. Nadie te va a decir nada.\n'
        '- Está prohibido generar mundo sin razón.\n'
        '- No está permitida la duplicación de ítems.\n Excepciones: bloques con gravedad, elitrós y esponjas.')\
        .add_field(name = '> Tareas de Proyectos:', inline = False, value = show_tasks(client))\
        .set_thumbnail(url = config['Thumbnail'])
    
    return embed

