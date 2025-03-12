from .Embeds import *
from .Views import *
from .Modules import *

async def discord_creator(client: McDisClient, *, loop: bool = False):
    channel = client.get_channel(config['Channel ID'])
    
    while True:  
        try:
            messages =  [msg async for msg in channel.history(limit = None, oldest_first = True)]
            
            if len(messages) == 0:
                await channel.send(embed = banner_es_embed(), view = banner_es_views())
                await channel.send(config['Discord Invite'])

            elif len(messages) == 2 and all([message.author.id == client.user.id for message in messages]):
                await messages[0].edit(embed = banner_es_embed(), view = banner_es_views())  
                
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

async def discord_extras(client: McDisClient):
    from .TicketSystem.Loader import load
    await load(client)

    from .Form.Loader import load
    await load(client)

    extensions = ["Banners.DiscordInfo.Behaviours"]
    
    for extension in extensions:
        if extension in client.extensions:
            await client.unload_extension(extension)
    
        await client.load_extension(extension)

    await client.tree.sync()
