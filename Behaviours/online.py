from __future__ import annotations

import discord
from Classes.AeServer import AeServer
from Classes.config import get_ae_config, get_ae_servers
from discord.ext import commands
from dismanager.classes import DisManagerClient

_EMBED_COLOUR = 0x2F3136


def _is_command(content: str, prefix: str, name: str) -> bool:
    stripped = content.strip()
    if not prefix or not stripped.startswith(prefix):
        return False
    command = stripped[len(prefix) :].split(maxsplit=1)[0].casefold()
    return command == name.casefold()


class OnlineBehaviour(commands.Cog):
    """Respond to ``online`` and ``bots`` commands in the ChatBridge channel."""

    def __init__(self, client: DisManagerClient) -> None:
        self.client = client

    def _servers(self) -> dict[str, AeServer]:
        return get_ae_servers(self.client)

    def _chatbridge_channel_id(self) -> int:
        return get_ae_config(self.client).chatbridge.channel_id

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot or message.channel.id != self._chatbridge_channel_id():
            return

        prefix = self.client.config.bot_prefix
        if _is_command(message.content, prefix, 'online'):
            description = ''.join(
                f'`[{server.name}]`: {", ".join(server.online_players)}\n\n'
                for server in self._servers().values()
            )
            await message.channel.send(
                embed=self._build_list_embed('Usuarios conectados:', description)
            )
        elif _is_command(message.content, prefix, 'bots'):
            description = ''.join(
                f'`[{server.name}]`: {", ".join(server.bots)}\n\n'
                for server in self._servers().values()
            )
            await message.channel.send(
                embed=self._build_list_embed('Bots:', description)
            )

    def _build_list_embed(self, title: str, description: str) -> discord.Embed:
        embed = discord.Embed(
            title=title,
            colour=_EMBED_COLOUR,
            description=description,
        )
        embed.set_thumbnail(url=get_ae_config(self.client).thumbnail)
        return embed


async def setup(client: DisManagerClient) -> None:
    """Register the OnlineBehaviour cog on ``client``."""
    await client.add_cog(OnlineBehaviour(client))
