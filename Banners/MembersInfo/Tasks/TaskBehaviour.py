from __future__ import annotations

import discord
from discord.ext import commands
from dismanager.classes import DisManagerClient

from .TaskLog import del_log, is_task


class TasksBehaviour(commands.Cog):
    """Keep task thread registry synced when threads are deleted or archived."""

    def __init__(self, client: DisManagerClient) -> None:
        self.client = client

    @commands.Cog.listener()
    async def on_raw_thread_delete(self, event: discord.RawThreadDeleteEvent) -> None:
        if event.thread is None or not is_task(event.thread):
            return
        del_log(event.thread)

    @commands.Cog.listener()
    async def on_thread_update(
        self,
        _before: discord.Thread,
        after: discord.Thread,
    ) -> None:
        if is_task(after) and after.archived:
            await after.edit(archived=False)


async def setup(client: DisManagerClient) -> None:
    """Register the TasksBehaviour cog on ``client``."""
    await client.add_cog(TasksBehaviour(client))
