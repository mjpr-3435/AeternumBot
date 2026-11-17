from __future__ import annotations

from dismanager.classes import DisManagerClient

from .FormViews import FormBannerView
from .LogInteraction import reactive_views, update_log


async def load(client: DisManagerClient) -> None:
    """Clean stale form entries and register persistent form views."""
    await update_log(client)
    client.add_view(FormBannerView(0, lang='es'))
    client.add_view(FormBannerView(0, lang='en'))
    await reactive_views(client)
