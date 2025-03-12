from ..Modules import *

def form_info_request       (form_id:int, request: list) -> tuple:
    df = pd.read_csv(form_log, index_col = 'index')
    ticket = df.loc[df['form_id'] == form_id]
    info = []
    for arg in request:
        info.append(ticket[arg].values[0])
    
    if len(request) == 1:
        return info[0]
    
    return tuple(info)

def form_info_update        (form_id:int, new_values: dict):
    df = pd.read_csv(form_log, index_col = 'index')
    for key, value in new_values.items():
        df.loc[df['form_id'] == form_id, key] = value
    df.to_csv(form_log)

def new_log                 (message: discord.Message, user_id: int):
    df = pd.read_csv(form_log, index_col = 'index')

    new_ticket = pd.DataFrame({'form_id': message.id,
                               'channel_id': message.channel.id,
                               'message_id': message.id,
                               'log_message_id': 0,
                               'owner_id': user_id}, index = [df.shape[0]])
    
    if df.shape[0] == 0:
        new_ticket.rename_axis('index').to_csv(form_log)
    else:
        df = pd.concat([df, new_ticket]).rename_axis('index')
        df.to_csv(form_log)

async def reactive_views(client: commands.Bot):
    from .FormViews import form_banner_views

    df = pd.read_csv(form_log)
    channels_id = df['channel_id'].to_list()
    messages_id = df['message_id'].to_list()
    owners_id = df['owner_id'].to_list()
    
    for i in range(len(channels_id)):
        try:
            form = await client.get_channel(channels_id[i]).fetch_message(messages_id[i])
            await form.edit(view = form_banner_views(owners_id[i]))
        except: pass

async def update_log        (client: commands.Bot):
    df = pd.read_csv(form_log, index_col = 'index')
    channels_id = df['channel_id'].values

    for channel_id in channels_id:
        channel = client.get_channel(channel_id)
        if channel == None: df = df[df['channel_id'] != channel_id]
    
    df.reset_index(drop = True, inplace = True)
    df.rename_axis('index', inplace = True)
    df.to_csv(form_log)