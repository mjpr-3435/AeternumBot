from __future__ import annotations

import discord


def is_admin(member: discord.Member) -> bool:
    """Return whether ``member`` has guild administrator permissions."""
    return member.guild_permissions.administrator


async def get_or_create_thread(
    name: str,
    channel: discord.TextChannel,
    *,
    public: bool = False,
) -> discord.Thread:
    """Find an active/archived thread named ``name`` in ``channel`` or create one."""
    target_name = name.strip()
    async for archived_thread in channel.archived_threads():
        if archived_thread.name == target_name:
            await archived_thread.edit(archived=False)
            return archived_thread

    existing = next((item for item in channel.threads if item.name == target_name), None)
    if existing is not None:
        return existing

    if not public:
        return await channel.create_thread(name=target_name)

    anchor = await channel.send('_')
    try:
        return await channel.create_thread(name=target_name, message=anchor)
    finally:
        await anchor.delete()
