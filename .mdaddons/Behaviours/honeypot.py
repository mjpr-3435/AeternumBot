import discord

from discord.ext import commands

from Banners.HoneyPot.Modules import *
from Banners.HoneyPot.Views import HoneyPotView
from mcdis_rcon.classes import McDisClient


class HoneyPotBehaviour(commands.Cog):
    def __init__(self, client: McDisClient):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or message.guild is None:
            return

        if message.channel.id != config["Channel ID"]:
            return

        await self.delete_honeypot_message(message)

        try:
            await message.author.ban(
                reason=config["Ban Reason"],
                delete_message_seconds=0,
            )
        except discord.HTTPException as error:
            register_honeypot_failed_ban(message, str(error))
            return

        register_honeypot_ban(message)
        await self.send_log_entry(message)
        await self.refresh_honeypot_counter()

    async def delete_honeypot_message(self, message: discord.Message):
        try:
            await message.delete()
        except discord.HTTPException:
            pass

    async def send_log_entry(self, message: discord.Message):
        channel = resolve_honeypot_channel(self.client)
        log_thread = await thread(config["Log Thread Name"], channel, public=True)
        await log_thread.send(embed=self.build_log_embed(message))

    def build_log_embed(self, message: discord.Message) -> discord.Embed:
        content = message.content.strip() or "[sin texto]"
        if len(content) > 1000:
            content = content[:997] + "..."

        embed = discord.Embed(
            title="HoneyPot Log",
            colour=config["Accent Color"],
            description=(
                f"Usuario baneado: {message.author.mention}\n"
                f"ID: `{message.author.id}`\n"
                f"Canal: <#{config['Channel ID']}>"
            ),
        )
        embed.add_field(name="Mensaje", value=content, inline=False)
        embed.set_thumbnail(url=message.author.display_avatar)
        return embed

    async def refresh_honeypot_counter(self):
        banner_message = await find_honeypot_banner_message(self.client)

        if banner_message is None:
            return

        await banner_message.edit(view=HoneyPotView())


async def setup(client: McDisClient):
    await client.add_cog(HoneyPotBehaviour(client))
