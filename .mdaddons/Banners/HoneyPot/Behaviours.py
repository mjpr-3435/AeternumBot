from .Modules import *

class honeypot_behaviours(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    async def honeypot_on_message                (message: discord.Message):
        if message.author.bot: 
            return
        elif message.channel.id == config['Channel ID']:
            await message.author.ban()

async def setup(client: commands.Bot):
    await client.add_cog(honeypot_behaviours(client))

