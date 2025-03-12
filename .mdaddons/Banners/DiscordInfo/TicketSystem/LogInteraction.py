from ..Modules import *

def is_ticket                (channel_id: int) -> bool:
    df = pd.read_csv(tickets_log, index_col = 'index')
    
    if not channel_id in df['ticket_channel_id'].values:
        return False
    return True

def new_log                 (ticket_banner: discord.Message, interaction: discord.Interaction):
    df = pd.read_csv(tickets_log, index_col = 'index')

    new_ticket = pd.DataFrame({'state': 'active',
                               'ticket_channel_id': ticket_banner.channel.id,
                               'ticket_banner_id': ticket_banner.id,
                               'owner_id': interaction.user.id,
                               'ticket_number': df.shape[0] + 1}, index = [df.shape[0]])
    
    if df.shape[0] == 0:
        new_ticket.rename_axis('index').to_csv(tickets_log)
    else:
        df = pd.concat([df, new_ticket]).rename_axis('index')
        df.to_csv(tickets_log)

def new_ticket_number       () -> int:
    df = pd.read_csv(tickets_log, index_col = 'index')
    return df.shape[0] + 1

def ticket_id_from_user        (user: discord.user) -> int:
    df = pd.read_csv(tickets_log, index_col = 'index')
    
    if not user.id in df.loc[df['state'] == 'active']['owner_id'].values:
        return 0
    return df.loc[(df['owner_id'] == user.id) & (df['state'] == 'active')]['ticket_channel_id'].values[0]

def ticket_info_request     (ticket_channel_id: int, request: list) -> tuple:
    df = pd.read_csv(tickets_log, index_col = 'index')
    ticket = df.loc[df['ticket_channel_id'] == ticket_channel_id]
    info = []
    for arg in request:
        info.append(ticket[arg].values[0])
    
    if len(request) == 1:
        return info[0]
    
    return tuple(info)

def ticket_info_update      (ticket_channel_id: int, new_values: dict):
    df = pd.read_csv(tickets_log, index_col = 'index')
    for key, value in new_values.items():
        df.loc[df['ticket_channel_id'] == ticket_channel_id, key] = value
    df.to_csv(tickets_log)
    
async def update_log        (client: commands.Bot):
    df = pd.read_csv(tickets_log, index_col = 'index')
    tickets_id = df.loc[(df['state'] == 'active')]['ticket_channel_id'].values

    for ticket_id in tickets_id:
        channel = client.get_channel(ticket_id)
        if channel == None:
            df.loc[df['ticket_channel_id'] == ticket_id, 'state'] = 'closed'

    df.to_csv(tickets_log)