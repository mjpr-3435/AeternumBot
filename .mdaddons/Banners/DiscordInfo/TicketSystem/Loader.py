from .LogInteraction import *
from .TicketViews import TicketBannerView
from ..Modules import *


async def load(client: commands.Bot):
    await update_log(client)
    client.add_view(TicketBannerView(lang='es'))
    client.add_view(TicketBannerView(lang='en'))

    df = pd.read_csv(tickets_log)
    active_rows = df.loc[df['state'] == 'active']

    for _, row in active_rows.iterrows():
        channel = client.get_channel(int(row['ticket_channel_id']))
        if channel is None:
            continue
        try:
            message = await channel.fetch_message(int(row['ticket_banner_id']))
            lang = str(row.get('lang', 'es')) if hasattr(row, 'get') else 'es'
            await message.edit(view=TicketBannerView(lang=lang))
        except:
            pass
