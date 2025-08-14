from .Embeds import *
from .Views import *
from .Modules import *

async def discord_creator(client: McDisClient, *, loop: bool = False):
    channel = client.get_channel(config['Channel ID'])
    
    while True:  
        try:
            guild = client.get_guild(839325517529612348)
            messages =  [msg async for msg in channel.history(limit = None, oldest_first = True)]
            
            if len(messages) == 0:
                await channel.send(embed = banner_es_embed(), view = banner_es_views())
                await channel.send(embed = other_discords())  
                await channel.send(embed = members_embed())  
                await channel.send(embed = autoroles_embed(), view = autoroles_views(guild))  
                await channel.send(config['Discord Invite'])

            elif len(messages) == 5 and all([message.author.id == client.user.id for message in messages]):
                await messages[0].edit(embed = banner_es_embed(), view = banner_es_views())  
                await messages[1].edit(embed = other_discords())  
                await messages[2].edit(embed = members_embed())  
                await messages[3].edit(embed = autoroles_embed(), view = autoroles_views(guild))  
                
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

async def discord_extras(client: McDisClient):
    from .TicketSystem.Loader import load
    await load(client)

    from .Form.Loader import load
    await load(client)

    extensions = ["Banners.DiscordInfo.Behaviours",
                  "Banners.DiscordInfo.MemberListCommand"]
    
    for extension in extensions:
        if extension in client.extensions:
            await client.unload_extension(extension)
    
        await client.load_extension(extension)

    await client.tree.sync()
