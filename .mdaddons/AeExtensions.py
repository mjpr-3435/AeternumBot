import discord
import asyncio
import shutil
import importlib
import sys
import os

from mcdis_rcon.classes import McDisClient, Network

class mdaddon():
    def __init__(self, client: McDisClient):
        self.client               = client
        self.persistent_tasks     = []
        self.config_mdplugins = \
            {   'SMP'           : ['manager.py', 'chatbridge.py', 'calc.py', 'join_motd_ae.py', 'here.py', 'execute.py', 'reg-bkps.py', 'scoreboard.py', 'tts_addon.py'],
                'CMP'           : ['manager.py', 'chatbridge.py', 'calc.py', 'join_motd_ae.py', 'here.py', 'op.py', 'tts_addon.py'                                     ],
                'MMP'           : ['manager.py', 'chatbridge.py', 'calc.py', 'join_motd_ae.py', 'here.py', 'op.py', 'reg-updater.py', 'tts_addon.py'                   ],
                'PMP'           : ['manager.py', 'chatbridge.py', 'calc.py', 'here.py', 'tts_addon.py'],
                'Dummy'         : ['manager.py', 'chatbridge.py', 'calc.py', 'here.py', 'tts_addon.py', 'dummy_manager.py'],
                'SMP 1.12'      : ['manager.py', 'chatbridge.py', 'calc.py', 'join_motd_ae.py', 'here.py', 'execute.py', 'reg-bkps.py', 'scoreboard.py', 'tts_addon.py']
                }
        
        ### Load Bot Related ###

        print('     -> Cargando AeExtensions')

        if not self.client.path_addons in sys.path: 
            sys.path.insert(0, self.client.path_addons)

        self.reload_modules()
        self.manage_mdplugins()
        self.update_server_classes()
        asyncio.create_task(self.load())
    
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
        from Banners.MembersInfo.Creator import members_creator, members_extras
        asyncio.create_task(members_extras          (self.client))
        task = asyncio.create_task(members_creator  (self.client))
        self.persistent_tasks.append(task)

        from Banners.DiscordInfo.Creator import discord_creator, discord_extras
        asyncio.create_task(discord_extras          (self.client))
        task = asyncio.create_task(discord_creator  (self.client))
        self.persistent_tasks.append(task)

        ### Status ###

        await self.client.change_presence(
            activity = discord.CustomActivity(
            name = 'Aeternum SMP',
            status = discord.Status.online)
        )
  
    def       reload_modules            (self):
        modules = [mod for mod in sys.modules if mod.startswith('Banners.') or mod.startswith('Classes.')]

        for mod in modules:
            try:
                importlib.reload(sys.modules[mod])
            except:
                pass
            
    def       manage_mdplugins          (self):
        available_mdplugins = os.listdir(os.path.join(self.client.path_addons, 'mdplugins'))

        for process in self.client.processes:
            if not process.name in self.config_mdplugins.keys():
                continue
            
            for plugin in os.listdir(process.path_plugins):
                plugin_path = os.path.join(process.path_plugins, plugin)
                if not os.path.isdir(plugin_path): os.remove(plugin_path)

            for plugin in self.config_mdplugins[process.name]:
                if not plugin in available_mdplugins: pass
                source = os.path.join(self.client.path_addons, 'mdplugins', plugin)
                dest   = os.path.join(process.path_plugins, plugin)

                shutil.copy(source, dest)
            
            process.load_plugins(reload = True)
      
    def       update_server_classes     (self):
        from Classes.AeServer import AeServer
        
        if any([x.is_running() for x in self.client.servers]): return
        
        self.client.processes   = [x for x in self.client.processes if isinstance(x, Network)]
        self.client.servers     = []

        for name in self.client.config['Processes']['Servers']:
            server = AeServer(name, self.client, self.client.config['Processes']['Servers'][name])
            self.client.processes.append(server)
            self.client.servers.append(server)
            print(f'        • {name} -> {server.__class__.__name__}')

    def       unload                    (self):
        for task in self.persistent_tasks:
            task.cancel()