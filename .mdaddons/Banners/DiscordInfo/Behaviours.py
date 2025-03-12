from .TicketSystem.LogInteraction import *
from .Form.LogInteraction import update_log
from .Form.FormCreation import *
from .Modules import *

from mcdis_rcon.classes import McDisClient
from discord.ext import commands

class TicketSystemBehaviour(commands.Cog):
    def __init__(self, client: McDisClient):
        self.client = client

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, reaction: discord.RawReactionActionEvent):
        if not is_ticket(reaction.channel_id): return
        if not ticket_info_request(reaction.channel_id, ['ticket_banner_id']) == reaction.message_id: return 
        elif reaction.member.bot: return

        ticket_channel = self.client.get_channel(reaction.channel_id)
        message = await ticket_channel.fetch_message(reaction.message_id)
        
        if   str(reaction.emoji) == '🔒':
            await message.clear_reactions()
            await message.edit(embed = message.embeds[0].add_field(name='', value = f'<@{reaction.member.id}> **confirma la eliminación del ticket**'))
            await message.add_reaction('✅')
            await message.add_reaction('❌')
        
        elif   str(reaction.emoji) == '📋':
            await form_creation(self.client, ticket_channel, reaction.user_id)
            user = self.client.get_user(reaction.user_id)
            await message.remove_reaction('📋', user)

        elif str(reaction.emoji) == '✅':
            await message.edit(embed=message.embeds[0].remove_field(-1).add_field(name='', value='**El ticket se eliminará en breve...**'))
    
            await ticket_channel.delete()
            ticket_info_update(ticket_channel.id, {'state':'closed'})
        
        elif str(reaction.emoji) == '❌':
            await message.edit(embed = message.embeds[0].remove_field(-1))
            await message.clear_reactions()
            await message.add_reaction('🔒')
            await message.add_reaction('📋')
        
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        if not is_ticket(channel.id): return
        
        ticket_info_update(channel.id, {'state':'closed'})
        await update_log(self.client)
    
async def setup(client: McDisClient):
    await client.add_cog(TicketSystemBehaviour(client))