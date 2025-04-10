import anvil
import os

from Classes.AeServer import AeServer
from mcdis_rcon.utils import clear_cmd

class mdplugin():
    def __init__(self, server: AeServer):
        self.server = server
        self.markers = {}

    async def on_player_command(self, player: str, message: str):
        if not player in self.markers.keys(): self.markers[player] = {'p1' : None,
                                                                      'p2' : None}
        
        if self.server.is_command(message, 'mdhelp'):
            self.server.show_command(player, 'mk help', 'Muestra los comandos del marker')

        elif self.server.is_command(message, 'mk help'):
            self.server.show_command(player, 'mk pos1',  'Establece la posición 1.')
            self.server.show_command(player, 'mk pos2',  'Establece la posición 2.')
            self.server.show_command(player, 'mk clear', 'Elimina los marcadores actuales.')

        elif self.server.is_command(message, 'mk pos1'):
            dim, pos = await self.add_marker(player, 'p1')
            file = self.pos_to_region(pos)

            self.read_region(os.path.join(self.server.path_files, 'server', 'world', 'region', file))

        elif self.server.is_command(message, 'mk pos2'):
            await self.add_marker(player, 'p2')

        elif self.server.is_command(message, 'mk clear'):
            self.server.execute(f'kill @e[tag={player}p1]')
            self.server.execute(f'kill @e[tag={player}p2]')
            self.markers[player] = {'p1' : None,
                                    'p2' : None}

    async def   add_marker(self, player: str, tag: str):
        self.server.execute(f'kill @e[tag={player}{tag}]')
        raw_pos = await self.server.get_data(player, 'Pos')
        raw_dim = await self.server.get_data(player, 'Dimension')

        raw_pos = raw_pos[raw_pos.find('[') + 1 : raw_pos.find(']')].split(',')
        dim     = raw_dim.replace('"','').split(':')[1]
        pos = tuple(int(float(x.strip()[:-1])) for x in raw_pos)

        x = int(float(raw_pos[0].strip()[:-1])) if float(raw_pos[0].strip()[:-1]) >= 0 else int(float(raw_pos[0].strip()[:-1]) - 1)
        y = int(float(raw_pos[1].strip()[:-1]))
        z = int(float(raw_pos[2].strip()[:-1])) if float(raw_pos[2].strip()[:-1]) >= 0 else int(float(raw_pos[2].strip()[:-1]) - 1)

        nbt = f'{{BlockState:{{Name:"minecraft:gray_stained_glass"}}, Glowing:1b, Invisible:1b,Invulnerable:1b,PersistenceRequired:1b,Silent:1b,NoGravity:1b,Time:1,DropItem:0b,HurtEntities:0b, Tags:["{player}{tag}"], CustomName:"\\"{player} | {tag}\\"", CustomNameVisible:1b}}'

        self.server.execute(f'execute in minecraft:{dim} run summon minecraft:falling_block {x} {y} {z} {nbt}')

        self.markers[player][tag] = f'{dim} : {pos}'
        
        return dim, pos

    def         read_region(self, region_path):
        clear_cmd()
        region = anvil.Region.from_file(region_path)
        print(region.chunk_data(0,0).keys())
        
        return
    
        for x in range(32):  # 32x32 chunks en una región
            for z in range(32):
                chunk = region.chunk_data(x,y)
                print(chunk)

    
    def         pos_to_region(self, pos : tuple):
        r_x = int(pos[0] // (32*16))
        r_z = int(pos[2] // (32*16))

        return f"r.{r_x}.{r_z}.mca"
