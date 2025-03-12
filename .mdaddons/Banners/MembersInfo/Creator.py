from .TaskLog import show_tasks
from .Modules import *

async def members_creator(client: McDisClient, loop: bool = True):
    channel = client.get_channel(config['Channel ID'])

    while True:
        try:
            messages        = [msg async for msg in channel.history(limit = None, oldest_first = True)]
            banner_image    = discord.File(os.path.join(os.path.dirname(__file__), 'Banner.png'))
            banner          = await banner_embed(client)

            if len(messages) == 0:
                await channel.send(embed = banner, file = banner_image)
            
            elif len(messages) == 1 and messages[0].author.id == client.user.id:
                await messages[0].edit(embed = banner)
            
            else:
                await channel.purge(limit = 100)
                continue

            if not loop: break

        except asyncio.CancelledError:
            return
        
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
            f'Ip 1.12:                                    '[:-len(config['Ip 1.12'])] + config['Ip 1.12'] + '\n'
            f'Ip Plugins:                                 '[:-len(config['IP Plugins'])] + config['IP Plugins'] + '\n'
            f'Seed:                                       '[:-len(config['Seed'])] + config['Seed'] + '```||\n')\
        .add_field(name = '', inline = True, value = f'<#{announcements.id}>')\
        .add_field(name = '', inline = True, value = active_days)\
        .add_field(name = '> Reglas para miembros', inline = False, value =
        '- No filtrar mensajes fuera del servidor.\n'
        '- No se tolerará ningún tipo de toxicidad.\n'
        '- Quien grifee el servidor será baneado permanente.\n'
        '- Si se llegara a romper una granja, AVISA. Nadie te va a decir nada.\n'
        '- Está prohibido generar mundo sin razón.\n'
        '- No está permitida la duplicación de ítems.\n Excepsiones: bloques con gravedad, elitrós y esponjas.')\
        .add_field(name = '> Tareas de Proyectos:', inline = False, value = show_tasks(client))\
        .set_thumbnail(url = config['Thumbnail'])
    
    return embed

