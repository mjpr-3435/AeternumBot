from mcdis_rcon.utils import isAdmin, mc_uuid
from mcdis_rcon.classes import McDisClient
from discord.ext import commands
from discord.app_commands import choices, Choice

import discord
import json
import os

class WhitelisterCommand(commands.Cog):
    def __init__(self, client: McDisClient):
        self.client = client
        self.interviewer_id = 914530780523401267

    @discord.app_commands.command(
        name            = 'whitelist',
        description     = 'Administra la whitelist del SMP'
    )
    @choices(action = [Choice(name = i, value = i) for i in ['Add', 'Remove']])

    async def whitelister_command(self,
        interaction: discord.Interaction, 
        action: Choice[str], 
        nickname: str):

        if not isAdmin(interaction.user) and not self.interviewer_id in [role.id for role in interaction.user.roles]:
            await interaction.response.send_message('✖ No tienes permisos.', ephemeral = True, delete_after = 1)
            return
        
        await interaction.response.defer(thinking = True, ephemeral = True)
        uuid = mc_uuid(player = nickname)

        if not uuid:
            await interaction.followup.send(content = f'✖ No existe el usuario `{nickname}` entre las cuentas premium de Minecraft.')
            return
        
        uuid = mc_uuid(player = nickname, online = False)
        server = next(filter(lambda x: x.name == 'SMP', self.client.servers), None)
        whitelist_json_path = os.path.join(server.path_files, 'server' 'whitelist.json')

        with open(whitelist_json_path, "r", encoding="utf-8") as file:
            whitelist = json.load(file)

        uuids = [entry["uuid"] for entry in whitelist]
        
        if action.value == 'Add':
            
            if uuid in uuids:
                embed = self.make_embed('El usuario ya estaba en la whitelist.', nickname, uuid)
            
            else:
                new_player = {"uuid" : uuid, "name" : nickname}
                whitelist.append(new_player)

                with open(whitelist_json_path, "w", encoding="utf-8") as file:
                    json.dump(whitelist, file, indent=2)

                server.execute('whitelist reload')

                embed = self.make_embed('Usuario añadido.', nickname, uuid)

        if action.value == 'Remove':
            if not uuid in uuids:
                embed = self.make_embed('El usuario no estaba en la whitelist.', nickname, uuid)
        
            else:
                whitelist = [entry for entry in whitelist if entry["uuid"] != uuid]

                with open(whitelist_json_path, "w", encoding="utf-8") as file:
                    json.dump(whitelist, file, indent=2)

                server.execute('whitelist reload')
                embed = self.make_embed('Usuario removido.', nickname, uuid)

        await interaction.followup.send(embed=embed)

    def    make_embed(self, content: str, nickname: str, uuid: str):
        embed = discord.Embed(
            title = "> **Whitelist SMP**",
            description =
                f"{content}\n"
                f"- **Username:** {nickname}\n"
                f"- **Offline UUID:** {uuid}",
            color = 0x2f3136)\
        .set_thumbnail(url=f"https://mc-heads.net/head/{nickname.lower()}.png")\
        .set_footer(text = 'Whitelist System \u200b', icon_url = self.client.user.display_avatar)
            
        return embed
    
async def setup(client: commands.Bot):
    await client.add_cog(WhitelisterCommand(client))
