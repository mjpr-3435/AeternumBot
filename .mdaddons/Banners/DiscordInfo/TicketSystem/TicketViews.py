from .TicketBanner import ticket_banner_embed
from .LogInteraction import ticket_info_request, ticket_info_update
from ..Form.FormCreation import form_creation
from ..Modules import *


class TicketBannerView(discord.ui.View):
    def __init__(self, lang: str = 'es'):
        super().__init__(timeout=None)
        self.lang = lang

        for child in self.children:
            if isinstance(child, discord.ui.Button):
                if child.custom_id == 'ticket:lang_toggle':
                    child.label = 'Es' if lang == 'en' else 'En'
                elif child.custom_id == 'ticket:form':
                    child.label = 'Apply' if lang == 'en' else 'Formulario'
                elif child.custom_id == 'ticket:close':
                    child.label = 'Close' if lang == 'en' else 'Cerrar'

    async def _guard_ticket(self, interaction: discord.Interaction):
        ticket_number = ticket_info_request(interaction.channel.id, ['ticket_number'])
        if ticket_number is not None:
            return ticket_number

        text = '✖ This ticket is no longer registered.' if self.lang == 'en' else '✖ Este ticket ya no está registrado.'
        await interaction.response.send_message(text, ephemeral=True, delete_after=5)
        return None

    @discord.ui.button(label='En', style=discord.ButtonStyle.gray, custom_id='ticket:lang_toggle')
    async def lang_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        ticket_number = await self._guard_ticket(interaction)
        if ticket_number is None:
            return

        new_lang = 'es' if self.lang == 'en' else 'en'
        ticket_info_update(interaction.channel.id, {'lang': new_lang})
        await interaction.response.edit_message(
            embed=ticket_banner_embed(interaction.user, ticket_number, lang=new_lang),
            view=TicketBannerView(lang=new_lang)
        )

    @discord.ui.button(label='Formulario', emoji='📋', style=discord.ButtonStyle.blurple, custom_id='ticket:form')
    async def form_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.bot:
            await interaction.response.defer()
            return

        ticket_number = await self._guard_ticket(interaction)
        if ticket_number is None:
            return

        owner_id = ticket_info_request(interaction.channel.id, ['owner_id'])
        if interaction.user.id != owner_id:
            msg = '✖ Only the ticket owner can open the form.' if self.lang == 'en' else '✖ Solo el dueño del ticket puede abrir su formulario.'
            await interaction.response.send_message(msg, ephemeral=True, delete_after=5)
            return

        await interaction.response.defer(ephemeral=True, thinking=True)
        await form_creation(interaction.client, interaction.channel, interaction.user.id, lang=self.lang)
        response_text = '✔ Form opened in this ticket.' if self.lang == 'en' else '✔ Formulario abierto en este ticket.'
        response = await interaction.followup.send(response_text)
        await response.delete(delay=20)

    @discord.ui.button(label='Cerrar', emoji='🔒', style=discord.ButtonStyle.red, custom_id='ticket:close')
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.bot:
            await interaction.response.defer()
            return

        ticket_number = await self._guard_ticket(interaction)
        if ticket_number is None:
            return

        embed = ticket_banner_embed(interaction.user, ticket_number, lang=self.lang)
        if self.lang == 'en':
            embed.add_field(name='> Confirmation', value=f'{interaction.user.mention} confirm if you want to close this ticket.', inline=False)
        else:
            embed.add_field(name='> Confirmación', value=f'{interaction.user.mention} confirma si deseas cerrar este ticket.', inline=False)
        await interaction.response.edit_message(embed=embed, view=TicketCloseConfirmView(lang=self.lang))


class TicketCloseConfirmView(discord.ui.View):
    def __init__(self, lang: str = 'es'):
        super().__init__(timeout=None)
        self.lang = lang

        for child in self.children:
            if isinstance(child, discord.ui.Button):
                if child.custom_id == 'ticket:close_confirm':
                    child.label = 'Confirm' if lang == 'en' else 'Confirmar'
                elif child.custom_id == 'ticket:close_cancel':
                    child.label = 'Cancel' if lang == 'en' else 'Cancelar'

    async def _guard_ticket(self, interaction: discord.Interaction):
        ticket_number = ticket_info_request(interaction.channel.id, ['ticket_number'])
        if ticket_number is not None:
            return ticket_number

        text = '✖ This ticket is no longer registered.' if self.lang == 'en' else '✖ Este ticket ya no está registrado.'
        await interaction.response.send_message(text, ephemeral=True, delete_after=5)
        return None

    @discord.ui.button(label='Confirmar', emoji='✅', style=discord.ButtonStyle.red, custom_id='ticket:close_confirm')
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        ticket_number = await self._guard_ticket(interaction)
        if ticket_number is None:
            return

        embed = ticket_banner_embed(interaction.user, ticket_number, lang=self.lang)
        if self.lang == 'en':
            embed.add_field(name='> Status', value='The ticket will close shortly...', inline=False)
        else:
            embed.add_field(name='> Estado', value='El ticket se cerrará en breve...', inline=False)
        await interaction.response.edit_message(embed=embed, view=None)
        ticket_info_update(interaction.channel.id, {'state': 'closed'})
        await interaction.channel.delete()

    @discord.ui.button(label='Cancelar', emoji='❌', style=discord.ButtonStyle.gray, custom_id='ticket:close_cancel')
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        ticket_number = await self._guard_ticket(interaction)
        if ticket_number is None:
            return

        await interaction.response.edit_message(
            embed=ticket_banner_embed(interaction.user, ticket_number, lang=self.lang),
            view=TicketBannerView(lang=self.lang)
        )
