from mcdis_rcon.utils import hover, extras
from Classes.AeServer import AeServer

class mdplugin():
    def __init__(self, server: AeServer):
        self.server = server
        # Mantener un set con jugadores que tienen glowing permanente
        self.tour_glowing = set()

    async def on_player_command(self, player: str, message: str):
        args = message.split()

        # Comando de ayuda
        if self.server.is_command(message, 'mdhelp'):
            self.server.show_command(player, 'loc help', 'Muestra los comandos de localización.')

        if self.server.is_command(message, 'loc help'):
            self.server.show_command(player, 'here', 'Muestra la posición del jugador.')
            self.server.show_command(player, 'where <player>', 'Muestra la posición de otro jugador.')
            self.server.show_command(player, f'glow <player | default : {player}>', 'Activa o desactiva glowing permanente (solo admins).')

        # Comando "here": muestra posición del propio jugador
        if self.server.is_command(message, 'here'):
            await self._show_position(player, player)

        # Comando "where": muestra posición de otro jugador
        if self.server.is_command(message, 'where') and len(args) > 1:
            input_name = args[1].lower()
            # Buscar entre jugadores y bots
            all_players = self.server.online_players + self.server.bots
            match = next((p for p in all_players if p.lower() == input_name), None)
            if match:
                await self._show_position(player, match)
            else:
                msg = extras([
                    hover('§c[✖] ', hover='Error'),
                    '{"text":"Jugador no encontrado.","color":"red"}'
                ])
                self.server.execute(f'tellraw {player} {msg}')

        # Comando "glow": toggle glowing permanente
        if self.server.is_command(message, 'glow'):
            target_name = player  # por defecto, el propio jugador
            if len(args) > 1:
                input_name = args[1].lower()
                all_players = self.server.online_players + self.server.bots
                match = next((p for p in all_players if p.lower() == input_name), None)
                if match:
                    target_name = match
                else:
                    msg = extras([
                        hover('§c[✖] ', hover='Error'),
                        '{"text":"Jugador no encontrado.","color":"red"}'
                    ])
                    self.server.execute(f'tellraw {player} {msg}')
                    return

            # Verificar permisos
            is_admin = player in self.server.admins
            if not is_admin and target_name != player:
                msg = extras([
                    hover('§c[✖] ', hover='Error'),
                    '{"text":"No puedes aplicar esto a otro jugador.","color":"red"}'
                ])
                self.server.execute(f'tellraw {player} {msg}')
                return

            # Toggle glowing
            if target_name in self.tour_glowing:
                self.server.execute(f'effect clear {target_name} minecraft:glowing')
                self.tour_glowing.remove(target_name)
                msg = extras([
                    hover('§e[◯] ', hover='Glow desactivado'),
                    '{"text":"Glowing permanente desactivado.","color":"yellow"}'
                ])
            else:
                self.server.execute(f'effect give {target_name} minecraft:glowing 1000000 0 true')
                self.tour_glowing.add(target_name)
                msg = extras([
                    hover('§a[✔] ', hover='Glow activado'),
                    '{"text":"Glowing permanente activado.","color":"green"}'
                ])

            self.server.execute(f'tellraw {player} {msg}')

    async def _show_position(self, requester: str, target: str):
        raw_pos = await self.server.get_data(target, 'Pos')
        raw_dim = await self.server.get_data(target, 'Dimension')

        raw_pos = raw_pos[raw_pos.find('[') + 1 : raw_pos.find(']')].split(',')
        dim1     = raw_dim.replace('"','').split(':')[1]

        color = {'overworld' : 'green', 'the_nether' : 'red', 'the_end' : 'yellow'}
        show_dim = {'overworld' : 'Overworld', 'the_nether' : 'Nether', 'the_end' : 'End'}

        if dim1 in ['overworld', 'the_nether']:
            pos1 = tuple(int(float(x.strip()[:-1])) for x in raw_pos)
            dim2 = 'the_nether' if dim1 == 'overworld' else 'overworld'

            if dim1 == 'overworld':
                pos2 = tuple(int(float(x.strip()[:-1])/8) for x in raw_pos)
            else:
                pos2 = tuple(int(float(x.strip()[:-1])*8) for x in raw_pos)

            message = extras([
                hover('[§k+X§r] ', color='dark_gray', hover='Qué miras?'),
                hover(f'[{pos1[0]}, {pos1[1]}, {pos1[2]}]', color=color[dim1], hover=show_dim[dim1]),
                '{"text":" -> ","color":"gray"}',
                hover(f'[{pos2[0]}, {pos1[1]}, {pos2[2]}]', color=color[dim2], hover=show_dim[dim2])
            ], text=f'@{target} ', color='gray')

        elif dim1 == 'the_end':
            pos1 = tuple(int(float(x.strip()[:-1])) for x in raw_pos)
            message = extras([
                hover('[§k+X§r] ', color='dark_gray', hover='Qué miras?'),
                hover(f'[{pos1[0]}, {pos1[1]}, {pos1[2]}]', color=color[dim1], hover=show_dim[dim1])
            ], text=f'@{target} ', color='gray')

        self.server.execute(f'tellraw @a {message}')
        self.server.execute(f'effect give {target} minecraft:glowing {10} 0 true')
