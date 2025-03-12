from .FormBanner import form_banner_embed
from .FormViews import form_banner_views
from .LogInteraction import *
from ..Modules import *
 
async def form_creation(client:commands.Bot, channel: discord.abc.GuildChannel, user_id: int):
    form = await channel.send(embed = form_banner_embed(client), view = form_banner_views(user_id))
    new_log(form, user_id)