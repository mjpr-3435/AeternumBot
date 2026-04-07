from .LogInteraction import *
from .FormViews import form_banner_views
from ..Modules import *

async def load(client: commands.Bot):
    await update_log(client)
    client.add_view(form_banner_views(0, lang='es'))
    client.add_view(form_banner_views(0, lang='en'))
    await reactive_views(client)
