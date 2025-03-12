from .LogInteraction import *
from ..Modules import *

async def load(client: commands.Bot):
    await update_log(client)