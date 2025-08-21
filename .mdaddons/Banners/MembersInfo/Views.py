from mcdis_rcon.utils import mc_uuid
from .Modules import *
from .Embeds import *

class banner_views(discord.ui.View):
    def __init__(self):
        super().__init__(timeout = None)

    @discord.ui.button(label = 'Whitelist',
                       style = discord.ButtonStyle.gray)
    async def whitelist_button(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(embed= whitelist_embed(), view = WhitelistListView(), ephemeral = True)

    @discord.ui.button(label = 'Proyectos',
                       style = discord.ButtonStyle.gray)
    async def proyectos_button(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(embeds = proyectos_embed(), ephemeral = True)

    @discord.ui.button(label = 'Perímetros',
                       style = discord.ButtonStyle.gray)
    async def perimetros_button(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(embeds = perimetros_embed(), ephemeral = True)

    @discord.ui.button(label = 'Decoraciones',
                       style = discord.ButtonStyle.gray)
    async def decoraciones_button(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(embeds = decoraciones_embed(), ephemeral = True)


class AddNicknameModal(discord.ui.Modal, title = "Agregar a la Whitelist"):
    nickname = discord.ui.TextInput(
        label="Nickname (Considera mayúsculas y minúsculas)",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        nickname = self.nickname.value.replace(" ","")
        df_whitelist_log = pd.read_csv(whitelist_log, index_col='index')

        if nickname in df_whitelist_log['nickname'].values:
            embed = make_embed(interaction.client, 'El usuario ya estaba en la whitelist.', nickname, interaction.user.mention)
            await interaction.followup.send(embed=embed)
            return

        df_new_log = pd.DataFrame({
            'nickname': [nickname],
            'user_id': [interaction.user.id],
            "date": "No Registrado"
        }, index=[df_whitelist_log.shape[0]])

        df_whitelist_log = pd.concat([df_whitelist_log, df_new_log])
        df_whitelist_log = df_whitelist_log.sort_values(by='nickname').reset_index(drop=True).rename_axis('index')

        df_whitelist_log.to_csv(whitelist_log)
        add_to_whitelist(nickname)
        update_whitelist_on_servers(interaction.client)

        embed = make_embed(interaction.client, 'Usuario añadido.', nickname, interaction.user.mention)
        await interaction.followup.send(embed=embed)
        await interaction.followup.edit_message(message_id=interaction.message.id, embed = whitelist_embed())

        channel = interaction.client.get_channel(config['Channel ID'])
        whitelist_log_thread = await thread('Whitelist Log', channel)
        await whitelist_log_thread.send(embed=embed)

class RemoveNicknameModal(discord.ui.Modal, title = "Remover de la Whitelist"):
    nickname = discord.ui.TextInput(
        label="Nickname (Considera mayúsculas y minúsculas)",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        nickname = self.nickname.value
        df = pd.read_csv(whitelist_log, index_col='index')

        if nickname not in df['nickname'].values:
            embed = make_embed(interaction.client, 'El usuario no estaba en la whitelist.', nickname, interaction.user.mention)
            await interaction.followup.send(embed=embed)
            return

        df = df[df['nickname'] != nickname]
        df.reset_index(drop=True, inplace=True)
        df.rename_axis('index', inplace=True)
        df.to_csv(whitelist_log)
        remove_from_whitelist(nickname)
        update_whitelist_on_servers(interaction.client)

        embed = make_embed(interaction.client, 'Usuario removido.', nickname, interaction.user.mention)
        await interaction.followup.send(embed=embed)
        await interaction.followup.edit_message(message_id=interaction.message.id, embed = whitelist_embed())

        channel         = interaction.client.get_channel(config['Channel ID'])
        whitelist_log_thread   = await thread('Whitelist Log', channel)
        await whitelist_log_thread .send(embed = embed)

def make_embed(client:McDisClient, content: str, nickname: str, edited_by: str):
    mc_uuid_online = mc_uuid(player=nickname, online=True)
    mc_uuid_offline = mc_uuid(player=nickname, online=False)

    embed = discord.Embed(
        title="> **Whitelist SMP**",
        description=(
            f"{content}\n"
            f"- **Username:** {nickname}\n"
            f"- **Online UUID:** {mc_uuid_online if not mc_uuid_online is None else 'El usuario no es Premium.'}\n"
            f"- **Offline UUID:** {mc_uuid_offline}\n"
            f"Editado por: {edited_by}\n"
        ),
        color=0x2f3136
    )
    embed.set_thumbnail(url=f"https://mc-heads.net/head/{nickname.lower()}.png")
    embed.set_footer(text='Whitelist System \u200b', icon_url = client.user.display_avatar)
    return embed

def add_to_whitelist(nickname: str) -> str:
    uuid_offline = mc_uuid(player=nickname, online=False)
    uuid_online = mc_uuid(player=nickname, online=True)

    with open(whitelist_path, 'r', encoding='utf-8') as f:
        whitelist = json.load(f)

    new_entries = []
    for uuid in filter(None, {uuid_offline, uuid_online}):
        if not any(entry["uuid"] == uuid for entry in whitelist):
            whitelist.append({"uuid": uuid, "name": nickname})
            new_entries.append(uuid)

    if not new_entries:
        return

    with open(whitelist_path, 'w', encoding='utf-8') as f:
        json.dump(whitelist, f, indent=2)

def remove_from_whitelist(nickname: str) -> str:
    with open(whitelist_path, 'r', encoding='utf-8') as f:
        whitelist = json.load(f)

    new_whitelist = [entry for entry in whitelist if entry["name"].lower() != nickname.lower()]
    removed_count = len(whitelist) - len(new_whitelist)

    if removed_count == 0:
        return

    with open(whitelist_path, 'w', encoding='utf-8') as f:
        json.dump(new_whitelist, f, indent=2)

def update_whitelist_on_servers(client:McDisClient):
    for server in client.servers:
        if server.name.lower() == 'overviewer': continue
        server_whitelist_path = os.path.join(server.path_files, 'server', 'whitelist.json')

        shutil.copy2(whitelist_path, server_whitelist_path)
        server.execute('whitelist reload')

class WhitelistListView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout = 300)
        self.len            = len(pd.read_csv(whitelist_log))
        self.max_page       = math.ceil(self.len/30)
        self.page           = 1
        
        self.add_item(UpdateButton())
        self.add_item(PreviousPageButton())
        self.add_item(NextPageButton())
        self.add_item(AddButton())
        self.add_item(RemoveButton())

    async def   _update_page       (self, interaction: discord.Interaction):
        if not interaction.response.is_done():
            await interaction.response.defer()

        await interaction.followup.edit_message(
            message_id = interaction.message.id,
            embed = whitelist_embed(self.page),
            view = self
        )
    
    async def   _update_interface (self, interaction: discord.Interaction):
        if not interaction.response.is_done():
            await interaction.response.defer()

        await interaction.followup.edit_message(
            message_id = interaction.message.id,
            embed = whitelist_embed(self.page),
            view = self
        )

class UpdateButton          (discord.ui.Button):

    def __init__(self):
        super().__init__(label='🔄', style=discord.ButtonStyle.gray)
        self.view : WhitelistListView

    async def callback(self, interaction: discord.Interaction):
        await self.view._update_page(interaction)

class PreviousPageButton    (discord.ui.Button):
    def __init__(self):
        super().__init__(label = '<', style = discord.ButtonStyle.gray)
        self.view : WhitelistListView

    async def callback(self, interaction: discord.Interaction):
        self.view.page = self.view.page - 1 if self.view.page > 1 else 1

        await self.view._update_page(interaction)
        
class NextPageButton        (discord.ui.Button):
    def __init__(self):
        super().__init__(label = '>', style = discord.ButtonStyle.gray)
        self.view : WhitelistListView

    async def callback(self, interaction: discord.Interaction):
        self.view.page = self.view.page + 1 if self.view.page < self.view.max_page else self.view.max_page

        await self.view._update_page(interaction)

class AddButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label = 'Add', style=discord.ButtonStyle.blurple)
        self.view : WhitelistListView

    async def callback(self, interaction: discord.Interaction):
        interviewer_id = 914530780523401267

        if not isAdmin(interaction.user) and not interviewer_id in [role.id for role in interaction.user.roles]:
            await interaction.response.send_message('✖ No tienes permisos.', ephemeral = True, delete_after = 1)
            return
        
        await interaction.response.send_modal(AddNicknameModal())

class RemoveButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label = 'Remove', style=discord.ButtonStyle.red)
        self.view : WhitelistListView

    async def callback(self, interaction: discord.Interaction):
        interviewer_id = 914530780523401267

        if not isAdmin(interaction.user) and not interviewer_id in [role.id for role in interaction.user.roles]:
            await interaction.response.send_message('✖ No tienes permisos.', ephemeral = True, delete_after = 1)
            return
        
        await interaction.response.send_modal(RemoveNicknameModal())


def whitelist_embed(page: int = 1, page_size: int = 30) -> discord.Embed:
    df = pd.read_csv(whitelist_log)
    df = df.sort_values('index').reset_index(drop=True)

    start = (page - 1) * page_size
    end = min(start + page_size, len(df))
    df_page = df.iloc[start:end]

    show_nick = '\n'.join(f'`{i + 1:>3}`‎ ‎ ‎ `{nick[:16]:>16}`' for nick, i in zip(df_page['nickname'], df_page['index']))
    show_user = '\n'.join(f'`🧧` <@{uid}>' for uid in df_page['user_id'])
    show_date = '\n'.join(f'`📆` {date}' for date in df_page['date'])

    embed = discord.Embed(color = 0x2f3136)
    embed.set_footer(icon_url='https://i.postimg.cc/XqQx5rT5/logo.png', text=f'Aeternum Whitelist')
    embed.add_field(inline=True, name='`  #`‎ ‎ ‎ **Usuario**', value=f'\n{show_nick}')
    embed.add_field(inline=True, name='**Añadido Por**', value=f'\n{show_user}')
    embed.add_field(inline=True, name='**Última Conexión**', value=f'\n{show_date}')

    return embed

