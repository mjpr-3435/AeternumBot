from .TicketSystem.LogInteraction import *
from .Form.LogInteraction import update_log
from .Modules import *

from mcdis_rcon.classes import McDisClient
from discord.ext import commands


class TicketSystemBehaviour(commands.Cog):
    def __init__(self, client: McDisClient):
        self.client = client

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        if not is_ticket(channel.id):
            return

        ticket_info_update(channel.id, {'state': 'closed'})
        await update_log(self.client)


async def setup(client: McDisClient):
    await client.add_cog(TicketSystemBehaviour(client))
