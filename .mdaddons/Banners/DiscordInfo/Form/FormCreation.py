from .FormBanner import form_banner_embed
from .FormViews import form_banner_views
from .LogInteraction import *
from ..Modules import *
 
async def form_creation(client:commands.Bot, channel: discord.abc.GuildChannel, user_id: int, lang: str = 'es'):
    form = await channel.send(embed = form_banner_embed(client, lang=lang), view = form_banner_views(user_id, lang=lang))
    new_log(form, user_id, lang=lang)
