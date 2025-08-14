import os
import discord
import math

from mcdis_rcon.utils import read_dat_files
from Classes.AeServer import AeServer

class mdplugin():
    def __init__(self, server: AeServer):
        self.server             = server
        self.scoreboards_len    = 30

    async def listener_on_message(self, message: discord.Message):
        if message.author.bot: return
        elif message.content.lower().strip() == '!!digs':
            scores      = self.digs_scores()
            dig_embed   = self.scoreboard_embed('Aeternum digs', scores)
            view        = ScoreboardView(self, 'Aeternum digs', scores)

            await message.channel.send(embed = dig_embed, view = view)

    def dig_format_value(self, value : int):
        magnitude = [ '', '🥝', '🍈', ]
        if not int(value/1000): i = 0
        elif not int(value/1000**2): i = 1
        else: i = 2

        if i:
            return f'{f"{value/1000**i:.2f}":>8} {magnitude[i]}'
        else:
            return f'{f"{int(value)}":>8} {magnitude[i]}'

    def digs_scores(self):
        path = os.path.join(self.server.path_files, 'server', 'world', 'data', 'scoreboard.dat')
        data = read_dat_files(path)

        bots = self.server.get_bot_log()
        scores = []
        total = 0 

        for x in data['data']['PlayerScores']:
            if x['Name'] in bots: continue

            elif x['Objective'] == 'dig-all': 
                score = int(x['Score'])
                if score == 0: continue
                
                scores.append({"player" : x['Name'], "score" : score})
                total += score

        scores.insert(0, {"player" : 'Total', "score" : total})

        return scores
    
    def scoreboard_embed(self, title : str, scores : list, page : int = 1):
        scores.sort(key = lambda x: x['score'], reverse = True)

        show_players = ''
        show_index   = ''

        for i in range(self.scoreboards_len*(page-1), min(self.scoreboards_len*(page) + 1, len(scores) + 1)): 
            show_index += f'{i if i!= 0 else "":>2}\n'
            show_players += f'{scores[i]["player"].capitalize():>16}\n'
        
        embed = discord.Embed(
            color = 0x2f3136
        ).set_footer(icon_url = 'https://i.postimg.cc/XqQx5rT5/logo.png', text = f'{title} [Top {self.scoreboards_len}]')\
        .add_field(inline = True, name = '‎ ‎ 🌐', value = f'```\n{show_index}\n```')\
        .add_field(inline = True, name = "**Player**", value = f'```\n{show_players}\n```')\
        .add_field(inline = True, name = "**Score**", value = '```yml\n' + "\n".join([self.dig_format_value(item['score']) for item in scores][self.scoreboards_len*(page-1): min(self.scoreboards_len*(page) + 1, len(scores) + 1)])  + '```')

        return embed    
    
class ScoreboardView(discord.ui.View):
    def __init__(self, mdplugin: mdplugin, title : str, scores: list):
        super().__init__(timeout = 300)
        self.mdplugin       = mdplugin
        self.title          = title
        self.scores         = scores
        self.max_page       = math.ceil(len(self.scores)/self.mdplugin.scoreboards_len)
        self.page           = 1
        
        self.add_item(PreviousPageButton())
        self.add_item(NextPageButton())

    async def   _update_page       (self, interaction: discord.Interaction):
        if not interaction.response.is_done():
            await interaction.response.defer()

        await interaction.followup.edit_message(
            message_id = interaction.message.id,
            embed = self.mdplugin.scoreboard_embed(self.title, self.scores, self.page),
            view = self
        )

    async def   _update_interface (self, interaction: discord.Interaction):
        if not interaction.response.is_done():
            await interaction.response.defer()

        self.scores         = self.mdplugin.digs_scores()
        self.max_page       = math.ceil(len(self.scores)/self.mdplugin.scoreboards_len)

        await interaction.followup.edit_message(
            message_id = interaction.message.id,
            embed = self.mdplugin.scoreboard_embed(self.title, self.scores, self.page),
            view = self
        )

class PreviousPageButton    (discord.ui.Button):
    def __init__(self):
        super().__init__(label = '<', style = discord.ButtonStyle.gray)
        self.view : ScoreboardView

    async def callback(self, interaction: discord.Interaction):
        self.view.page = self.view.page - 1 if self.view.page > 1 else 1

        await self.view._update_page(interaction)
        
class NextPageButton        (discord.ui.Button):
    def __init__(self):
        super().__init__(label = '>', style = discord.ButtonStyle.gray)
        self.view : ScoreboardView

    async def callback(self, interaction: discord.Interaction):
        self.view.page = self.view.page + 1 if self.view.page < self.view.max_page else self.view.max_page

        await self.view._update_page(interaction)