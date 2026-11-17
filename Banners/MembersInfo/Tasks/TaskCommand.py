from __future__ import annotations

import discord
from discord import app_commands
from discord.app_commands import Choice, choices, describe
from discord.ext import commands
from dismanager.classes import DisManagerClient

from Classes import get_ae_config
from Utils.discord_helpers import is_admin

from ..Creator import members_creator
from .TaskLog import del_log, is_task, new_log


class TaskCommand(commands.Cog):
    """Admin-only slash command to create or close project task threads."""

    def __init__(self, client: DisManagerClient) -> None:
        self.client = client

    @app_commands.command(
        name='task',
        description='Administra los hilos de tareas',
    )
    @describe(
        name='Nombre del hilo de tareas',
        action='Acción que quieres hacer con el hilo',
    )
    @choices(action=[Choice(name=opt, value=opt) for opt in ('Create', 'Close')])
    async def task_command(
        self,
        interaction: discord.Interaction,
        action: Choice[str],
        name: str,
    ) -> None:
        if not isinstance(interaction.user, discord.Member) or not is_admin(interaction.user):
            await interaction.response.send_message(
                '✖ No tienes permisos.',
                ephemeral=True,
                delete_after=1,
            )
            return

        await interaction.response.defer(ephemeral=True)
        channel_id = get_ae_config(self.client).members_info.channel_id
        channel = self.client.get_channel(channel_id)
        if not isinstance(channel, discord.TextChannel):
            await interaction.followup.send('✖ Canal de MembersInfo no encontrado.')
            return

        matches = [
            thread
            for thread in channel.threads
            if thread.name.casefold() == name.casefold() and is_task(thread)
        ]

        if action.value == 'Create':
            if matches:
                await interaction.followup.send('✖ Ya existe una tarea con ese nombre.')
                return
            anchor = await channel.send('Hilo público creado.')
            thread = await anchor.create_thread(name=name.strip())
            await anchor.delete()
            new_log(thread)
            await members_creator(self.client, loop=False)
            await interaction.followup.send('✔')
        elif action.value == 'Close':
            if not matches:
                await interaction.followup.send('✖ No existe una tarea con ese nombre.')
                return
            thread = matches[0]
            await thread.delete()
            del_log(thread)
            await members_creator(self.client, loop=False)
            await interaction.followup.send('✔')


async def setup(client: DisManagerClient) -> None:
    """Register the TaskCommand cog on ``client``."""
    await client.add_cog(TaskCommand(client))
