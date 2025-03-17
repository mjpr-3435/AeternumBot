from mcdis_rcon.utils import hover, extras
from Classes.AeServer import AeServer

class mdplugin():
    def __init__(self, server: AeServer):
        self.server = server

    async def on_player_command(self, player: str, message: str):
        if self.server.is_command(message, 'mdhelp'):
            self.server.show_command(player, 'here', 'Muestra la posición del jugador.')

        if self.server.is_command(message, 'here'):
            raw_pos : str = await self.server.get_data(player, 'Pos')
            raw_dim : str = await self.server.get_data(player, 'Dimension')

            raw_pos = raw_pos[raw_pos.find('[') + 1 : raw_pos.find(']')].split(',')
            dim1     = raw_dim.replace('"','').split(':')[1]

            color = {'overworld' : 'green', 'the_nether' : 'red', 'the_end' : 'yellow'}
            show_dim = {'overworld' : 'Overworld', 'the_nether' : 'Nether', 'the_end' : 'End'}

            if dim1 in ['overworld', 'the_nether']:
                pos1 = tuple(int(float(x.strip()[:-1])) for x in raw_pos)
                dim2 = 'the_nether' if dim1 == 'overworld' else 'overworld'

                if dim1 == 'overworld':
                    pos2 = tuple(int(float(x.strip()[:-1])/8) for x in raw_pos)
                elif dim1 == 'the_nether':
                    pos2 = tuple(int(float(x.strip()[:-1])*8) for x in raw_pos)


                message = extras([  hover('[§k+X§r] ', color = 'dark_gray', hover = 'Qué miras?'),
                                    hover(f'[{pos1[0]}, {pos1[1]}, {pos1[2]}]', color = color[dim1], hover = show_dim[dim1]), 
                                    '{"text" : " -> ", "color" : "gray"}',
                                    hover(f'[{pos2[0]}, {pos1[1]}, {pos2[2]}]', color = color[dim2], hover = show_dim[dim2])],
                                    text = f'@{player} ', color = 'gray')
            
            elif dim1 == 'the_end':
                pos1 = tuple(int(float(x.strip()[:-1])) for x in raw_pos)

                message = extras([  hover('[§k+X§r] ', color = 'dark_gray', hover = 'Qué miras?'),
                                    hover(f'[{pos1[0]}, {pos1[1]}, {pos1[2]}]', color = color[dim1], hover = show_dim[dim1])],
                                    text = f'@{player} ', color = 'gray')
            
            message = message.replace('\n','')
            self.server.execute(f'tellraw @a {message}')
            self.server.execute(f'effect give {player} minecraft:glowing {10} 0 true')