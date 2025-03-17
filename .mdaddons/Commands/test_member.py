from mcdis_rcon.utils import isAdmin
from discord.ext import commands
from discord.app_commands import choices, Choice

import discord

class TestMemberCommand(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.interviewer_id = 914530780523401267
        self.test_member_id = 859477794052374540
        self.members_id     = 889357182297071636
        self.member_id      = 843606159880749137

    @discord.app_commands.command(
        name            = 'test_member',
        description     = 'Dar roles a los miembros de prueba'
    )        
    @choices(action = [Choice(name = i, value = i) for i in ['Grant', 'Revoke', 'Promote']])

    async def test_member_command(self,
        interaction: discord.Interaction, 
        action: Choice[str], 
        member: discord.Member):

        if not isAdmin(interaction.user) and not self.interviewer_id in [role.id for role in interaction.user.roles]:
            await interaction.response.send_message('✖ No tienes permisos.', ephemeral = True, delete_after = 1)
            return
        
        await interaction.response.defer(thinking = True, ephemeral = True)

        if action.value == 'Grant':
            if self.member_id in [role.id for role in member.roles]:
                await interaction.followup.send('✖ Solo puedes usar esto con miembros nuevos.')
                return
            
            await self.add_role(member, self.members_id)
            await self.add_role(member, self.test_member_id)

        elif action.value == 'Revoke':
            if not self.test_member_id in [role.id for role in member.roles]:
                await interaction.followup.send('✖ Solo puedes usar esto con miembros a prueba.')
                return
            
            await self.remove_role(member, self.members_id)
            await self.remove_role(member, self.test_member_id)

        elif action.value == 'Promote':
            if not self.test_member_id in [role.id for role in member.roles]:
                await interaction.followup.send('✖ Solo puedes usar esto con miembros a prueba.')
                return
            
            await self.remove_role(member, self.test_member_id)
            await self.add_role(member, self.member_id)

        await interaction.followup.send('✔')

    async def add_role(self, member: discord.Member, role_id: int):
        role = member.guild.get_role(role_id)
        if role and role not in member.roles:
            await member.add_roles(role)

    async def remove_role(self, member: discord.Member, role_id: int):
        role = member.guild.get_role(role_id)
        if role and role in member.roles:
            await member.remove_roles(role)

async def setup(client: commands.Bot):
    await client.add_cog(TestMemberCommand(client))
