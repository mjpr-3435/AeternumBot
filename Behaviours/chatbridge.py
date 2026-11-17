from __future__ import annotations

import discord
from discord.ext import commands
from dismanager.classes import DisManagerClient

from Classes import get_ae_config, get_ae_servers


class ChatBridgeBehaviour(commands.Cog):
    """Relay Discord messages from the ChatBridge channel to online Minecraft servers."""

    def __init__(self, client: DisManagerClient) -> None:
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return

        cb_channel_id = get_ae_config(self.client).chatbridge.channel_id
        if message.channel.id != cb_channel_id:
            return

        sanitized = message.content.replace('\n', ' ').replace('"', "'")
        for server in get_ae_servers(self.client).values():
            if server.online_players or server.bots:
                server.send_response('@a', f'[DIS] <{message.author.display_name}> {sanitized}')


async def setup(client: DisManagerClient) -> None:
    """Register the ChatBridgeBehaviour cog on ``client``."""
    await client.add_cog(ChatBridgeBehaviour(client))
