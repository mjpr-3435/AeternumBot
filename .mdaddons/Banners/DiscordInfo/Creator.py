from .Embeds import *
from .Views import *
from .Modules import *

async def discord_creator(client: McDisClient, *, loop: bool = False):
    channel = client.get_channel(config['Channel ID'])
    await extras_creator(client)
    await showcase_creator(client)
    await patreon_creator(client)

    while True:  
        try:
            messages =  [msg async for msg in channel.history(limit = None, oldest_first = True)]
            
            if len(messages) == 0:
                await channel.send(embed = banner_es_embed(), view = banner_es_views())
                await channel.send(config['Discord Invite'])

            elif len(messages) == 2 and all([message.author.id == client.user.id for message in messages]):
                await messages[0].edit(embed = banner_es_embed(), view = banner_es_views())   
                await messages[1].edit(content=config['Discord Invite'])   
                
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

async def extras_creator(client: McDisClient):
    channel = client.get_channel(config['Extras ID'])
    guild = client.get_guild(839325517529612348)
    messages =  [msg async for msg in channel.history(limit = None, oldest_first = True)]
    
    if len(messages) == 0:
        await channel.send(embed = other_discords())  
        await channel.send(embed = members_embed())  
        await channel.send(embed = autoroles_embed(), view = autoroles_views(guild))  

    elif len(messages) == 3 and all([message.author.id == client.user.id for message in messages]):
        await messages[0].edit(embed = other_discords())  
        await messages[1].edit(embed = members_embed())  
        await messages[2].edit(embed = autoroles_embed(), view = autoroles_views(guild))


async def patreon_creator(client: McDisClient):
    channel = client.get_channel(1426128088760324116)
    messages =  [msg async for msg in channel.history(limit = None, oldest_first = True)]
    
    if len(messages) == 0:
        await channel.send(embed = patreon_embed(), view = PatreonMenu())

    elif len(messages) == 1 and all([message.author.id == client.user.id for message in messages]):
        await messages[0].edit(embed = patreon_embed(), view = PatreonMenu())

async def showcase_creator(client: McDisClient):
    channel = client.get_channel(config['Showcase ID'])
    showcase_dir_path = os.path.join(os.path.dirname(__file__), 'Showcase')

    messages =  [msg async for msg in channel.history(limit = None, oldest_first = True)]
    i = 0
    for key, value in showcase_config.items():
        project_image_path = os.path.join(showcase_dir_path, f'{key}.png')
        project_image = discord.File(project_image_path)

        if not len(messages) > i:
            msg = await channel.send(content = f'> **{value}:**', file = project_image)
            await msg.create_thread(
                name=f"{value}: Imágenes Extra"
            )

            await msg.add_reaction(config['Emoji Server'])
        else:
            await messages[i].edit(attachments = [project_image])

        i += 1

async def discord_extras(client: McDisClient):
    from .TicketSystem.Loader import load
    await load(client)

    from .Form.Loader import load
    await load(client)

    extensions = ["Banners.DiscordInfo.Behaviours",
                  "Banners.DiscordInfo.MembersListCommand"]
    
    for extension in extensions:
        if extension in client.extensions:
            await client.unload_extension(extension)
    
        await client.load_extension(extension)

    await client.tree.sync()
