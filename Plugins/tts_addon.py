from __future__ import annotations

import discord
from dismanager.classes import BasePlugin, ManagedProcess

from Classes import AeServer, get_ae_config, get_ae_servers


class plugin(BasePlugin):
    """Relay subscribed players' in-game chat messages to the Discord TTS webhook."""

    process: ManagedProcess
    server: AeServer
    webhook: discord.Webhook | None
    active_players: list[str]

    def __init__(self, process: ManagedProcess) -> None:
        self.process = process
        self.server = get_ae_servers(process.client)[process.name.casefold()]
        self.webhook = None
        self.active_players = []

    async def on_plugins_load(self) -> None:
        tts_cfg = get_ae_config(self.process.client).tts
        channel = self.process.client.get_channel(tts_cfg.channel_id)
        if not isinstance(channel, discord.TextChannel):
            return

        webhooks = await channel.webhooks()
        self.webhook = next((wh for wh in webhooks if wh.name == tts_cfg.webhook_name), None)

    async def on_mc_player_command(self, player: str, message: str) -> None:
        if self.server.is_command(message, 'mdhelp'):
            self.server.show_command(player, 'tts', 'Todos tus mensajes serán enviados al canal.')
            return

        if self.server.is_command(message, 'tts'):
            if player in self.active_players:
                self.active_players.remove(player)
                self.server.send_response(player, f'§8@{player} §7-> §c[Desuscrito]')
                return

            self.active_players.append(player)
            self.server.send_response(player, f'§8@{player} §7-> §a[Suscrito]')

    async def on_mc_player_message(self, player: str, message: str) -> None:
        if self.webhook is None:
            return
        if player in self.active_players and not message.startswith(self.server.prefix):
            await self.webhook.send(
                message,
                username=player,
                avatar_url=f'https://mc-heads.net/head/{player.lower()}.png',
            )

    async def on_mc_player_left(self, player: str) -> None:
        if player in self.active_players:
            self.active_players.remove(player)
