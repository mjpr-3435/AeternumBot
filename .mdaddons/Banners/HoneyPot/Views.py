from .Embeds import honey_pot_en_embed
from .Modules import *


class HoneyPotView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        for child in self.children:
            if isinstance(child, discord.ui.Button) and child.custom_id == "honeypot:bee_counter":
                child.label = f" {get_honeypot_ban_count()}"
                child.disabled = False

    @discord.ui.button(
        label="En",
        style=discord.ButtonStyle.gray,
        custom_id="honeypot:lang_en",
        row=0,
    )
    async def en_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            embed= await honey_pot_en_embed(interaction.client),
            ephemeral=True,
        )

    @discord.ui.button(
        label=" 0",
        emoji=config["Bee Emoji"],
        style=discord.ButtonStyle.gray,
        custom_id="honeypot:bee_counter",
        row=0,
    )
    async def bee_counter_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
