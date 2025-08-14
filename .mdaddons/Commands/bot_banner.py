from mcdis_rcon.utils import isAdmin
from discord.ext import commands

import discord
import psutil

class BotBannerCommand(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @discord.app_commands.command(
            name            = 'bot_banner',
            description     = 'Banner del bot')
    async def help_command(self, interaction: discord.Interaction):
        if not isAdmin(interaction.user):
            await interaction.response.send_message('✖ No tienes permisos.', ephemeral = True, delete_after = 1)
            return
        
        await interaction.response.send_message(embed = self.embed(), ephemeral = True)

    def embed(self) -> discord.Embed:
        bot_ram_used = f'{psutil.Process().memory_info().rss/(1024**2)-23.5:.1f} MB'
        emoji_github                = '<:GitHub:1403731008758743213>'
        emoji_discord               = '<:AeDiscord:1390864678540017739>'
        emoji_discord_py            = '<:DiscordPy:1403731051259494552>'
        emoji_emoji_list            = '🧧'
        emoji_profiles_mc           = '<:KassiuLo:1403623720584613979>'

        link_developer_portal       = 'https://discord.com/developers/applications/775597340336586792/information'
        link_emoji_list             = 'https://es.piliapp.com/emoji/list/'
        link_ds_py_api              = 'https://discordpy.readthedocs.io/en/stable/api.html'
        link_ds_py_interactions_api = 'https://discordpy.readthedocs.io/en/stable/interactions/api.html'
        link_discord_markdown       = 'https://gist.github.com/matthewzring/9f7bbfd102003963f9be7dbcf7d40e51'
        link_github                 = 'https://github.com'
        link_default_thumbnail      = 'https://i.postimg.cc/XqQx5rT5/logo.png'
        link_profiles_mc            = 'https://minecraftpfp.com'

        commands = '\n'.join([f'/{command.name}' for command in self.client.tree.get_commands(type = discord.AppCommandType.chat_input)])
        
        embed = discord.Embed(
                title = f'> {self.client.user.display_name}',
                colour = 0x2f3136,
                description = 
                f'')\
            .add_field(name =            '', inline =  True, value = 
                f'{emoji_discord} DeveloperPortal\n'
                f'{emoji_github} Github\n'
                f'{emoji_github} Discord Markdown\n'
                f'{emoji_discord_py} Discord.py API\n'
                f'{emoji_discord_py} Discord.py Interactions API\n'
                f'{emoji_emoji_list} Emoji List\n'
                f'{emoji_profiles_mc} Profiles MC\n')\
            .add_field(name =            '', inline =  True, value = 
                f'[[Developer Portal]]({link_developer_portal})\n'
                f'[[GitHub Link]]({link_github})\n'
                f'[[Markdown Link]]({link_discord_markdown})\n'
                f'[[Discord.py API]]({link_ds_py_api})\n'
                f'[[Discord.py Interactions API]]({link_ds_py_interactions_api})\n'
                f'[[Emoji List Link]]({link_emoji_list})\n'
                f'[[Profiles MC]]({link_profiles_mc})\n')\
            .add_field(name =            '', inline =  False, value = '')\
            .add_field(name =     'Comando', inline =  True, value = commands)\
            .set_thumbnail(url = link_default_thumbnail)
        
        commands = '\n'.join([f'{command.name}' for command in self.client.tree.get_commands(type = discord.AppCommandType.message)])
    
        embed.add_field(name = 'Menus contextuales', inline =  True, value = commands)\
        .add_field(name = f'> **{self.client.user.name}**', inline = False, value=
                f'```asciidoc\n'
                f'Ram Usage::                                 '[:-len(bot_ram_used)] + bot_ram_used + '```')\

        return embed

async def setup(client: commands.Bot):
    await client.add_cog(BotBannerCommand(client))
