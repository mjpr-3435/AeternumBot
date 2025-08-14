from .TicketSystem.TicketCreator import ticket_creation
from .Embeds import *
from .Modules import *

class banner_en_views(discord.ui.View):
    def __init__(self):
        super().__init__(timeout = 900)

    @discord.ui.button(label = 'Server Info',
                       emoji = config['Emoji Server'],
                       style = discord.ButtonStyle.gray)
    async def server_info_button(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(embed = hardware_info_en_embed(), ephemeral = True)
        
    @discord.ui.button(label = 'Apply',
                       emoji = config['Emoji Server'],
                       style = discord.ButtonStyle.gray)
    async def apply_button(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(embeds = apply_en_embed(), ephemeral = True)
    
    @discord.ui.button(label = 'Rules',
                       emoji = config['Emoji Server'],
                       style = discord.ButtonStyle.gray)
    async def rules_button(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(embeds = rules_en_embed(), ephemeral = True)

    @discord.ui.button(label = 'Tickets',
                       emoji = '📩',
                       style = discord.ButtonStyle.blurple)
    async def form_button(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(thinking = True, ephemeral = True)
        
        if interaction.user.id in blacklist:
            response = await interaction.followup.send(f'✖ You are not allowed to open a ticket.')
            await response.delete(delay = 60)
            return
        
        ticket, created_ticket = await ticket_creation(interaction)

        if not created_ticket:
            response = await interaction.followup.send(f'✖ You already have an open ticket. <#{ticket.id}>')
            await response.delete(delay = 60)

        else:
            response = await interaction.followup.send(f'Ticket created <#{ticket.id}>.')
            await response.delete(delay = 60)

class banner_es_views(discord.ui.View):
    def __init__(self):
        super().__init__(timeout = None)

    @discord.ui.button(label = 'En',
                       emoji = config['Emoji Server'],
                       style = discord.ButtonStyle.gray)
    async def en_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(embed = banner_en_embed(), ephemeral = True, view = banner_en_views())

    @discord.ui.button(label = 'Server Info',
                       emoji = config['Emoji Server'],
                       style = discord.ButtonStyle.gray)
    async def server_info_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(embed = hardware_info_es_embed(), ephemeral = True)
        
    @discord.ui.button(label = 'Apply',
                       emoji = config['Emoji Server'],
                       style = discord.ButtonStyle.gray)
    async def apply_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(embeds = apply_es_embed(), ephemeral = True)
    
    @discord.ui.button(label = 'Rules',
                       emoji = config['Emoji Server'],
                       style = discord.ButtonStyle.gray)
    async def rules_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(embeds = rules_es_embed(), ephemeral = True)

    @discord.ui.button(label = 'Tickets',
                       emoji = '📩',
                       style = discord.ButtonStyle.blurple)
    async def form_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(thinking = True, ephemeral = True)

        if interaction.user.id in blacklist:
            response = await interaction.followup.send(f'✖ No estás permitido de abrir un ticket.')
            await response.delete(delay = 60)
            return

        ticket, created_ticket = await ticket_creation(interaction)

        if not created_ticket:
            response = await interaction.followup.send(f'✖ Ya tienes un ticket abierto. <#{ticket.id}>')
            await response.delete(delay = 5)
        
        else:
            response = await interaction.followup.send(f'Ticket creado <#{ticket.id}>.')
            await response.delete(delay = 60)

import discord

class autoroles_views(discord.ui.View):
    def __init__(self, guild: discord.Guild):
        super().__init__(timeout=None)
        self.roles_ids = autoroles_ids

        for child in self.children:
            if isinstance(child, discord.ui.Button):
                key = child.custom_id
                if key in self.roles_ids:
                    role = guild.get_role(self.roles_ids[key])
                    if role:
                        child.label = f" {len(role.members)}"

    async def update_button_label(self, button: discord.ui.Button, role: discord.Role):
        """Actualiza el label del botón con el número de miembros del rol."""
        button.label = f" {len(role.members)}"

    async def toggle_role(self, interaction: discord.Interaction, key: str, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True, thinking=True)

        role_id = self.roles_ids.get(key)
        role = interaction.guild.get_role(role_id)
        member = interaction.user

        if role in member.roles:
            await member.remove_roles(role)
            await interaction.followup.send(f"Te has **desuscrito** de `{role.name}`", ephemeral=True)
        else:
            await member.add_roles(role)
            await interaction.followup.send(f"Te has **suscrito** a `{role.name}`", ephemeral=True)

        await self.update_button_label(button, role)
        await interaction.message.edit(view=self)

    @discord.ui.button(label=" 0", style=discord.ButtonStyle.gray, emoji="📅", custom_id="eventos")
    async def btn_eventos(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.toggle_role(interaction, "eventos", button)

    @discord.ui.button(label=" 0", style=discord.ButtonStyle.gray, emoji="<:AeTwitch:1390864664791093319>", custom_id="twitch")
    async def btn_twitch(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.toggle_role(interaction, "twitch", button)

    @discord.ui.button(label=" 0", style=discord.ButtonStyle.gray, emoji="🎊", custom_id="nuevo_contenido")
    async def btn_nuevo(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.toggle_role(interaction, "nuevo_contenido", button)

    @discord.ui.button(label=" 0", style=discord.ButtonStyle.gray, emoji="📌", custom_id="anuncios")
    async def btn_anuncios(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.toggle_role(interaction, "anuncios", button)

    @discord.ui.button(label=" 0", style=discord.ButtonStyle.gray, emoji="📮", custom_id="todo")
    async def btn_todo(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.toggle_role(interaction, "todo", button)
