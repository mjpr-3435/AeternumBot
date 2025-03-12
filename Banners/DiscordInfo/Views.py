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
        ticket, created_ticket = await ticket_creation(interaction)

        if not created_ticket:
            response = await interaction.followup.send(f'✖ You already have an open ticket. <#{ticket.id}>')
            await response.delete(delay = 60)
            return
        
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
        ticket, created_ticket = await ticket_creation(interaction)

        if not created_ticket:
            response = await interaction.followup.send(f'✖ Ya tienes un ticket abierto. <#{ticket.id}>')
            await response.delete(delay = 5)
            return
        
        response = await interaction.followup.send(f'Ticket creado <#{ticket.id}>.')
        await response.delete(delay = 60)