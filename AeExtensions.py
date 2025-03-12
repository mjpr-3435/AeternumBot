import discord
import asyncio
import sys
import os

from mcdis_rcon.classes import McDisClient, Network

class mdaddon():
    def __init__(self, client: McDisClient):
        self.client               = client
        self.persistent_tasks     = []
        
        print('     -> Cargando AeExtensions')

        if not self.client.path_addons in sys.path: 
            sys.path.insert(0, self.client.path_addons)

            ### Load Bot Related ###

            asyncio.create_task(self.load())

        self.update_server_classes()
    
    async def load                      (self):

        ### Commands, ContextMenus, Behaviours ###

        cogs = ['Commands', 'ContextMenus', 'Behaviours']

        for cog in cogs:
            cog_path = os.path.join(self.client.path_addons, cog)
            os.makedirs(cog_path, exist_ok = True)
            scripts = [file.removesuffix('.py') for file in os.listdir(cog_path) if file.endswith('.py')]

            for script in scripts:
                extension = f"{cog}.{script}"
    
                if extension in self.client.extensions:
                    await self.client.unload_extension(extension)

                await self.client.load_extension(extension)
        
        await self.client.tree.sync()


        ### Banners ###
        
        from Banners.FriendsDiscords.Creator import friends_creator
        asyncio.create_task(friends_creator         (self.client))

        from Banners.MembersInfo.Creator import members_creator, members_extras
        asyncio.create_task(members_extras          (self.client))
        task = asyncio.create_task(members_creator  (self.client))
        self.persistent_tasks.append(task)

        from Banners.DiscordInfo.Creator import discord_creator, discord_extras
        asyncio.create_task(discord_extras          (self.client))
        task = asyncio.create_task(discord_creator  (self.client))
        self.persistent_tasks.append(task)

        ### Status ###
        
        initial_status = discord.Activity(
            type = discord.ActivityType.custom,
            name = "Aeternum SMP"
        )
        
        await self.client.change_presence(
            activity=initial_status,
            status=discord.Status.online
        )
    
    def       update_server_classes     (self):
        from Classes.AeServer import AeServer
        
        if all([isinstance(x, AeServer) for x in self.client.servers]): return

        self.client.processes   = [x for x in self.client.processes if isinstance(x, Network)]
        self.client.servers     = []

        for name in self.client.config['Processes']['Servers']:
            server = AeServer(name, self.client, self.client.config['Processes']['Servers'][name])
            self.client.processes.append(server)
            self.client.servers.append(server)
            print(f'        • {name} -> {server.__class__.__name__}')

    def       unload                    (self):
        return
    
        for task in self.persistent_tasks:
            task.cancel()