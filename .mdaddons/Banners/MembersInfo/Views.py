from mcdis_rcon.utils import mc_uuid
from .Modules import *
from .Embeds import *

INTERVIEWER_ID = 889357182297071636

class banner_views(discord.ui.View):
    def __init__(self):
        super().__init__(timeout = None)

        self.add_item(
            discord.ui.Button(
                label="Guía de Aeternum",
                style=discord.ButtonStyle.link,
                url="https://1drv.ms/f/c/084c1940e0b695f3/IgCRDTCc3IsuQI503WeNsyFuAYkjl6chCYuO3vrX6ZFhYfQ?e=lab3kc"
            )
        )

    @discord.ui.button(label = 'Whitelist',
                       style = discord.ButtonStyle.gray)
    async def whitelist_button(self, interaction:discord.Interaction, button: discord.ui.Button):
        has_interviewer_role = INTERVIEWER_ID in [role.id for role in interaction.user.roles]

        await interaction.response.send_message(
            embed=whitelist_embed(),
            view=WhitelistListView(is_admin_request=isAdmin(interaction.user) or has_interviewer_role),
            ephemeral=True
        )

    @discord.ui.button(label = 'Server Jobs',
                       style = discord.ButtonStyle.gray)
    async def apoyo_button(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(embeds = apoyo_embed(), ephemeral = True)

    @discord.ui.button(label = 'Twitch',
                       style = discord.ButtonStyle.gray)
    async def twitch_button(self, interaction:discord.Interaction, button: discord.ui.Button):
        embed, files = twitch_embed()
        await interaction.response.send_message(embed = embed, files = files, ephemeral = True)

class AddNicknameModal(discord.ui.Modal, title = "Agregar a la Whitelist"):
    nickname = discord.ui.TextInput(
        label="Nickname (Considera mayúsculas y minúsculas)",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        nickname = self.nickname.value.replace(" ","")
        df_whitelist_log = pd.read_csv(whitelist_log, index_col='index')
        inactives_only = _message_is_inactives_mode(interaction.message)

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
        await interaction.followup.edit_message(
            message_id=interaction.message.id,
            embed=whitelist_embed(inactives_only=inactives_only)
        )

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
        inactives_only = _message_is_inactives_mode(interaction.message)

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
        await interaction.followup.edit_message(
            message_id=interaction.message.id,
            embed=whitelist_embed(inactives_only=inactives_only)
        )

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
    def __init__(self, is_admin_request: bool = False):
        super().__init__(timeout = 300)
        self.is_admin_request = is_admin_request
        self.only_inactives = False
        self.len = 0
        self.max_page = 1
        self.page           = 1

        self._refresh_pagination()
        self.add_item(UpdateButton())
        if self.is_admin_request:
            self.add_item(InactivesToggleButton())
            self.add_item(WhitelistActionSelect())
        self.add_item(PreviousPageButton())
        self.add_item(NextPageButton())

    def _refresh_pagination(self):
        self.len = len(_get_whitelist_dataframe(self.only_inactives))
        self.max_page = max(1, math.ceil(self.len / 30))
        self.page = min(max(self.page, 1), self.max_page)

    async def   _update_page       (self, interaction: discord.Interaction):
        self._refresh_pagination()

        if not interaction.response.is_done():
            await interaction.response.defer()

        await interaction.followup.edit_message(
            message_id = interaction.message.id,
            embed = whitelist_embed(self.page, inactives_only=self.only_inactives),
            view = self
        )
    
    async def   _update_interface (self, interaction: discord.Interaction):
        self._refresh_pagination()

        if not interaction.response.is_done():
            await interaction.response.defer()

        await interaction.followup.edit_message(
            message_id = interaction.message.id,
            embed = whitelist_embed(self.page, inactives_only=self.only_inactives),
            view = self
        )

class UpdateButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label='🔄', style=discord.ButtonStyle.gray, row=1)
        self.view : WhitelistListView

    async def callback(self, interaction: discord.Interaction):
        await self.view._update_page(interaction)

class PreviousPageButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label = '<', style = discord.ButtonStyle.gray, row=1)
        self.view : WhitelistListView

    async def callback(self, interaction: discord.Interaction):
        self.view.page = self.view.page - 1 if self.view.page > 1 else 1
        await self.view._update_page(interaction)
        
class NextPageButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label = '>', style = discord.ButtonStyle.gray, row=1)
        self.view : WhitelistListView

    async def callback(self, interaction: discord.Interaction):
        self.view.page = self.view.page + 1 if self.view.page < self.view.max_page else self.view.max_page
        await self.view._update_page(interaction)

class InactivesToggleButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label='All', style=discord.ButtonStyle.green, row=1)
        self.view : WhitelistListView

    async def callback(self, interaction: discord.Interaction):
        if not isAdmin(interaction.user):
            await interaction.response.send_message('✖ No tienes permisos.', ephemeral=True, delete_after=1)
            return

        self.view.only_inactives = not self.view.only_inactives
        self.view.page = 1
        self.label = 'Inactives' if self.view.only_inactives else 'All'
        self.style = discord.ButtonStyle.gray if self.view.only_inactives else discord.ButtonStyle.green
        await self.view._update_interface(interaction)

class WhitelistActionSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label='Agregar', value='add', description='Añadir un usuario a la whitelist'),
            discord.SelectOption(label='Remover', value='remove', description='Eliminar un usuario de la whitelist'),
            discord.SelectOption(label='Purgar', value='purge', description='Eliminar inactivos de la whitelist'),
        ]
        super().__init__(
            placeholder='Acciones de whitelist',
            min_values=1,
            max_values=1,
            options=options,
            row=0
        )
        self.view : WhitelistListView

    async def callback(self, interaction: discord.Interaction):
        has_interviewer_role = INTERVIEWER_ID in [role.id for role in interaction.user.roles]
        is_admin = isAdmin(interaction.user)
        action = self.values[0]

        if action == 'add':
            if not is_admin and not has_interviewer_role:
                await interaction.response.send_message('✖ No tienes permisos.', ephemeral = True, delete_after = 1)
                return
            await interaction.response.send_modal(AddNicknameModal())
            return

        if action == 'remove':
            if not is_admin and not has_interviewer_role:
                await interaction.response.send_message('✖ No tienes permisos.', ephemeral = True, delete_after = 1)
                return
            await interaction.response.send_modal(RemoveNicknameModal())
            return

        if action == 'purge':
            if not is_admin:
                await interaction.response.send_message('✖ No tienes permisos.', ephemeral=True, delete_after=1)
                return
            await interaction.response.send_modal(PurgeInactivesModal(self.view))

class PurgeInactivesModal(discord.ui.Modal, title="Purge Inactives"):
    confirmation = discord.ui.TextInput(
        label='Escribe PURGE para confirmar',
        placeholder='PURGE',
        required=True
    )
    exclusions = discord.ui.TextInput(
        label='Excluir nombres',
        required=False,
        style=discord.TextStyle.paragraph
    )

    def __init__(self, whitelist_view: WhitelistListView):
        super().__init__()
        self.whitelist_view = whitelist_view

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)

        if self.confirmation.value.strip().upper() != 'PURGE':
            await interaction.followup.send('✖ Confirmación inválida. Debes escribir `PURGE`.', ephemeral=True)
            return

        excluded_nicknames = _parse_exclusion_lines(self.exclusions.value)
        removed_nicknames, excluded_applied = purge_inactive_whitelist_entries(excluded_nicknames)
        update_whitelist_on_servers(interaction.client)

        if removed_nicknames:
            preview = ', '.join(removed_nicknames[:20])
            if len(removed_nicknames) > 20:
                preview += ', ...'
            await interaction.followup.send(
                (
                    f'✔ Purge completado. Removidos: **{len(removed_nicknames)}**\n'
                    f'`{preview}`'
                    + (
                        f"\nExcluidos aplicados: **{len(excluded_applied)}**"
                        if excluded_applied else
                        (f"\nExclusiones recibidas: **{len(excluded_nicknames)}** (sin coincidencias inactivas)" if excluded_nicknames else "")
                    )
                ),
                ephemeral=True
            )
        else:
            await interaction.followup.send('✔ No hay inactivos para eliminar.', ephemeral=True)

        channel = interaction.client.get_channel(config['Channel ID'])
        whitelist_log_thread = await thread('Whitelist Log', channel)
        action_embed = discord.Embed(
            title='> **Whitelist SMP**',
            description=(
                f"Purge de inactivos ejecutado.\n"
                f"- **Removidos:** {len(removed_nicknames)}\n"
                f"- **Nombres removidos:** {_format_nickname_list(removed_nicknames)}\n"
                f"- **Excluidos aplicados:** {_format_nickname_list(excluded_applied)}\n"
                f"- **Editado por:** {interaction.user.mention}\n"
            ),
            color=0x2f3136
        )
        action_embed.set_footer(text='Whitelist System \u200b', icon_url=interaction.client.user.display_avatar)
        await whitelist_log_thread.send(embed=action_embed)

        await self.whitelist_view._update_interface(interaction)

def _get_whitelist_dataframe(inactives_only: bool = False) -> pd.DataFrame:
    df = pd.read_csv(whitelist_log)
    df = df.sort_values('index').reset_index(drop=True)

    if not inactives_only:
        return df

    cutoff_date = pd.Timestamp.now() - pd.DateOffset(months=3)
    parsed_dates = pd.to_datetime(df['date'], format='%Y-%m-%d', errors='coerce')
    inactive_mask = parsed_dates.isna() | (parsed_dates < cutoff_date)
    return df[inactive_mask].reset_index(drop=True)

def _message_is_inactives_mode(message: discord.Message | None) -> bool:
    if not message or not message.embeds:
        return False
    footer = message.embeds[0].footer
    footer_text = (footer.text or "") if footer else ""
    return 'Inactives' in footer_text

def _parse_exclusion_lines(raw_text: str | None) -> list[str]:
    if not raw_text:
        return []
    return [line.strip() for line in raw_text.splitlines() if line.strip()]

def _format_nickname_list(names: list[str], limit: int = 25) -> str:
    if not names:
        return 'Ninguno'
    shown = names[:limit]
    text = ', '.join(shown)
    if len(names) > limit:
        text += f', ... (+{len(names) - limit})'
    return text

def purge_inactive_whitelist_entries(excluded_nicknames: list[str] | None = None) -> tuple[list[str], list[str]]:
    df = pd.read_csv(whitelist_log, index_col='index')
    inactive_df = _get_whitelist_dataframe(inactives_only=True)

    if inactive_df.empty:
        return [], []

    excluded_nicknames_lc = {str(nick).lower() for nick in (excluded_nicknames or [])}
    excluded_applied = []
    if excluded_nicknames_lc:
        excluded_applied = (
            inactive_df[inactive_df['nickname'].astype(str).str.lower().isin(excluded_nicknames_lc)]['nickname']
            .dropna()
            .astype(str)
            .tolist()
        )
        inactive_df = inactive_df[
            ~inactive_df['nickname'].astype(str).str.lower().isin(excluded_nicknames_lc)
        ].reset_index(drop=True)

    if inactive_df.empty:
        return [], excluded_applied

    removed_nicknames = inactive_df['nickname'].dropna().astype(str).tolist()
    removed_nicknames_lc = {nick.lower() for nick in removed_nicknames}

    df = df[~df['nickname'].astype(str).str.lower().isin(removed_nicknames_lc)]
    df.reset_index(drop=True, inplace=True)
    df.rename_axis('index', inplace=True)
    df.to_csv(whitelist_log)

    with open(whitelist_path, 'r', encoding='utf-8') as f:
        whitelist = json.load(f)

    new_whitelist = [
        entry for entry in whitelist
        if str(entry.get("name", "")).lower() not in removed_nicknames_lc
    ]

    if len(new_whitelist) != len(whitelist):
        with open(whitelist_path, 'w', encoding='utf-8') as f:
            json.dump(new_whitelist, f, indent=2)

    return removed_nicknames, excluded_applied

def whitelist_embed(page: int = 1, page_size: int = 30, inactives_only: bool = False) -> discord.Embed:
    df = _get_whitelist_dataframe(inactives_only=inactives_only)

    start = (page - 1) * page_size
    end = min(start + page_size, len(df))
    df_page = df.iloc[start:end]

    if df_page.empty:
        show_nick = '`---`'
        show_user = '`---`'
        show_date = '`---`'
    else:
        show_nick = '\n'.join(f'`{i + 1:>3}`‎ ‎ ‎ `{nick[:16]:>16}`' for nick, i in zip(df_page['nickname'], df_page['index']))
        show_user = '\n'.join(f'`🧧` <@{uid}>' for uid in df_page['user_id'])
        show_date = '\n'.join(f'`📆` {date}' for date in df_page['date'])

    embed = discord.Embed(color = 0x2f3136)
    footer_mode = 'Inactives' if inactives_only else 'All'
    embed.set_footer(icon_url='https://i.postimg.cc/XqQx5rT5/logo.png', text=f'Aeternum Whitelist | {footer_mode}')
    embed.add_field(inline=True, name='`  #`‎ ‎ ‎ **Usuario**', value=f'\n{show_nick}')
    embed.add_field(inline=True, name='**Añadido Por**', value=f'\n{show_user}')
    embed.add_field(inline=True, name='**Última Conexión**', value=f'\n{show_date}')

    return embed

