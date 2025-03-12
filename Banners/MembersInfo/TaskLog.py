from .Modules import *

def is_task              (thread: discord.Thread)    -> bool:
    df_tasks_log = pd.read_csv(tasks_log, index_col = 'index')

    if thread.id in df_tasks_log['thread_id'].values:
        return True
    return False

def del_log             (thread: discord.Thread)    -> None:
    df_tasks_log = pd.read_csv(tasks_log, index_col = 'index')
    df_tasks_log = df_tasks_log[df_tasks_log['thread_id'] != thread.id]
    df_tasks_log.reset_index(drop = True, inplace = True)
    df_tasks_log.rename_axis('index', inplace = True)
    df_tasks_log.to_csv(tasks_log)
    
def new_log             (thread: discord.Thread)    -> None:
    df_tasks_log = pd.read_csv(tasks_log, index_col = 'index')

    df_new_log = pd.DataFrame({'thread_id': thread.id}, index = [df_tasks_log.shape[0]])
    if df_tasks_log.shape[0] == 0:
        df_new_log.rename_axis('index').to_csv(tasks_log)
    else:
        df_tasks_log = pd.concat([df_tasks_log,df_new_log]).rename_axis('index')
        df_tasks_log.to_csv(tasks_log)

def show_tasks                (client: commands.Bot)      -> str:
    df_tasks_log = pd.read_csv(tasks_log, index_col = 'index')
    threads_id = df_tasks_log['thread_id'].values

    for thread_id in threads_id:
        thread = client.get_channel(thread_id)
        if thread == None:
            indices = np.where(threads_id == thread_id)
            threads_id = np.delete(threads_id, indices)
        
    show_projects = ' • '.join([f'<#{thread_id}>' for thread_id in threads_id])

    return show_projects
    
async def update_log    (client: commands.Bot)      -> None:
    df_tasks_log = pd.read_csv(tasks_log, index_col = 'index')
    threads_id = df_tasks_log['thread_id'].values

    for thread_id in threads_id:
        try:
            thread = await client.fetch_channel(thread_id)
            await thread.edit(archived = False)
        except:
            df_tasks_log = df_tasks_log[df_tasks_log['thread_id'] != thread_id]

    df_tasks_log.reset_index(drop=True, inplace=True)
    df_tasks_log.rename_axis('index', inplace=True)
    df_tasks_log.to_csv(tasks_log)
