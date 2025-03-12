from .TaskLog import *
from .Modules import *

from mcdis_rcon.classes import McDisClient
from discord.ext import commands

class TasksBehaviour(commands.Cog):
    def __init__(self, client: McDisClient):
        self.client = client

    @commands.Cog.listener()
    async def on_raw_thread_delete(self, deleteEvent: discord.RawThreadDeleteEvent):
        if deleteEvent.thread == None:
            return
        if not is_task(deleteEvent.thread): return

        del_log(deleteEvent.thread)

    @commands.Cog.listener()
    async def on_thread_update(self, before_thread: discord.Thread, after_thread: discord.Thread):
        if is_task(after_thread):
            await after_thread.edit(archived = False)
    
async def setup(client: McDisClient):
    await client.add_cog(TasksBehaviour(client))