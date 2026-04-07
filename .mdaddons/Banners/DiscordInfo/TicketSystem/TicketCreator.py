from .TicketBanner import ticket_banner_embed
from .TicketViews import TicketBannerView
from .LogInteraction import *
from ..Modules import *


async def ticket_creation(interaction: discord.Interaction, lang: str = 'es') -> tuple[discord.TextChannel, bool]:
    ticket_id = ticket_id_from_user(interaction.user)
    if ticket_id:
        return interaction.client.get_channel(ticket_id), False

    guild = interaction.guild
    category_raw = [category for category in interaction.guild.categories if category.id == tickets_config['Category ID']]
    category = category_raw[0] if category_raw else None

    interviewer = [role for role in guild.roles if role.id == tickets_config['Ticket Moderator ID']]
    ticket_number = new_ticket_number()

    ticket_permissions = discord.PermissionOverwrite(
        read_messages=True,
        send_messages=True,
        create_public_threads=True,
        send_messages_in_threads=True
    )

    permissions = {
        interaction.user: ticket_permissions,
        guild.default_role: discord.PermissionOverwrite(read_messages=False)
    }

    if interviewer:
        permissions[interviewer[0]] = ticket_permissions

    created_ticket = await guild.create_text_channel(
        f'ticket-{interaction.user.display_name}',
        category=category,
        overwrites=permissions
    )

    ticket_banner = await created_ticket.send(
        content=interaction.user.mention,
        embed=ticket_banner_embed(interaction.user, ticket_number, lang=lang),
        view=TicketBannerView(lang=lang)
    )

    new_log(ticket_banner, interaction)
    ticket_info_update(created_ticket.id, {'lang': lang})
    return created_ticket, True
