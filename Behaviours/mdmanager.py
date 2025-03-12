from mcdis_rcon.classes import McDisClient
from Classes.AeServer import AeServer
from discord.ext import commands
import shutil
import os

class MdmanagerBehaviour(commands.Cog):
    def __init__(self, client: McDisClient):
        self.client = client
        
        self.config_mdplugins = \
            {   'SMP'           : ['manager.py', 'chatbridge.py', 'join_motd_ae.py', 'here.py', 'execute.py', 'reg-bkps.py', 'scoreboard.py'   ],
                'CMP'           : ['manager.py', 'chatbridge.py', 'join_motd_ae.py', 'here.py', 'op.py'                                        ],
                'MMP'           : ['manager.py', 'chatbridge.py', 'join_motd_ae.py', 'here.py', 'op.py', 'reg-updater.py'                      ],
                'PMP'           : ['manager.py', 'chatbridge.py', 'here.py']}

        self.manage_mdplugins()

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
    
async def setup(client: McDisClient):
    await client.add_cog(MdmanagerBehaviour(client))
