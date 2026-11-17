from __future__ import annotations

from dismanager.classes import DisManagerClient

from MaterialLists.material_lists import MaterialListsCog as BaseMaterialListsCog


class MaterialListsCog(BaseMaterialListsCog):
    """Slash commands and views for Aeternum material lists."""


async def setup(client: DisManagerClient) -> None:
    """Register the MaterialLists cog on ``client``."""
    await client.add_cog(MaterialListsCog(client))
