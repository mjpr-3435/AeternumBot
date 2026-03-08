import asyncio
import os
import math
import re

from Classes.AeServer import AeServer

class mdplugin():
    def __init__(self, server: AeServer):
        self.server = server
        self.player_positions       = {}
        self.max_region_blocks      = 10_000_000

        self._requested_block_data = None
        self._waiting_block_request = False
        
        for msg in (
            "The target block is not a block entity",
            "has the following block data"
        ):
            if msg not in self.server.blacklist:
                self.server.blacklist.append(msg)

        self.reg_bkps_dir = os.path.join(self.server.path_plugins, 'finder')
        os.makedirs(self.reg_bkps_dir, exist_ok = True)

        self.disable_command_feedback()

    async def   on_player_command(self, player: str, message: str):
        if player not in self.player_positions:
            self.player_positions[player] = {
                'overworld':  {'pos1': None, 'pos2': None},
                'the_nether': {'pos1': None, 'pos2': None},
                'the_end':    {'pos1': None, 'pos2': None},
            }
        
        if self.server.is_command(message, 'mdhelp'):

            if not player in self.server.admins: return
            self.server.show_command(player, 'fd help', 'Muestra los comandos del finder')

        elif self.server.is_command(message, 'fd help'):

            if not player in self.server.admins: return
            self.server.show_command(player, 'fd pos1', 'Establece la posición 1.')
            self.server.show_command(player, 'fd pos2', 'Establece la posición 2.')
            self.server.show_command(player, 'fd new-place <name>', 'Crea un registro de todos los cofres en la región y los guarda con nombre <name>.')

        elif self.server.is_command(message, 'search-on'):
            args = message.removeprefix(f'{self.server.prefix}search-on').strip().split()

            if len(args) < 2:
                self.server.send_response(player, "§c✖§f Uso: search-on <name> <item>")
                return

            name = args[0]
            item = " ".join(args[1:]).strip().lower()

            await self._search_on_place(player, name, item)
            return

        elif not player in self.server.admins:
            return
        
        elif self.server.is_command(message, 'fd pos1'):
            pos, dim = await self.get_player_position(player)

            self.player_positions[player][dim]['pos1'] = pos
            self.server.send_response(player, f"✔ Pos1 establecida")

            if self.player_positions[player][dim]['pos2']:
                await self._send_region_size_feedback(
                    player,
                    dim,
                    self.player_positions[player][dim]['pos1'],
                    self.player_positions[player][dim]['pos2']
                )

        elif self.server.is_command(message, 'fd pos2'):
            pos, dim = await self.get_player_position(player)

            self.player_positions[player][dim]['pos2'] = pos
            self.server.send_response(player, f"✔ Pos2 establecida")

            if self.player_positions[player][dim]['pos1']:
                await self._send_region_size_feedback(
                    player,
                    dim,
                    self.player_positions[player][dim]['pos1'],
                    self.player_positions[player][dim]['pos2']
                )

        elif self.server.is_command(message, 'fd clear'):
            self.player_positions[player] = {'pos1': None, 'pos2': None}
            self.server.send_response(player, f"✔ Posiciones limpias")
            
        elif self.server.is_command(message, 'fd new-place'):
            name = message.removeprefix(f'{self.server.prefix}fd new-place').strip().replace(" ", "")

            if not name:
                self.server.send_response(player, "✖ Debes proveer un nombre.")
                return

            pos, dim = await self.get_player_position(player)

            pos1 = self.player_positions[player][dim]['pos1']
            pos2 = self.player_positions[player][dim]['pos2']

            if pos1 is None or pos2 is None:
                self.server.send_response(player, "✖ Debes establecer pos1 y pos2 en esta dimensión.")
                return

            xmin, xmax, ymin, ymax, zmin, zmax = self._region_bounds(pos1, pos2)
            total_blocks = (xmax - xmin + 1) * (ymax - ymin + 1) * (zmax - zmin + 1)

            if total_blocks > self.max_region_blocks:
                self.server.send_response(
                    player,
                    f"✖ Región demasiado grande ({total_blocks} bloques). Límite: {self.max_region_blocks}."
                )
                return

            region_by_chunk = {}

            for x in range(xmin, xmax + 1):
                for y in range(ymin, ymax + 1):
                    for z in range(zmin, zmax + 1):
                        chunk_x = x // 16
                        chunk_z = z // 16
                        key = (chunk_x, chunk_z)

                        if key not in region_by_chunk:
                            region_by_chunk[key] = []

                        region_by_chunk[key].append((x, y, z))

            await self._scan_region_for_block_entities(name, dim, region_by_chunk)
    
    async def   _send_region_size_feedback(self, player: str, dim, pos1, pos2):
        xmin, xmax, ymin, ymax, zmin, zmax = self._region_bounds(pos1, pos2)
        asyncio.create_task(
            self._show_region_wireframe(xmin, xmax, ymin, ymax, zmin, zmax, dim)
        )

        total_blocks = (xmax - xmin + 1) * (ymax - ymin + 1) * (zmax - zmin + 1)

        if total_blocks > self.max_region_blocks:
            self.server.send_response(
                player,
                f"§e⚠§f Región: §e{total_blocks}§f bloques. Límite recomendado: §e{self.max_region_blocks}§f."
            )
        else:
            self.server.send_response(
                player,
                f"§7Región: §f{total_blocks}§7 bloques."
            )
    
    def         _region_bounds(self, pos1, pos2):
        def to_block(p):
            x = math.floor(p[0])
            y = math.floor(p[1])
            z = math.floor(p[2])
            return (x, y, z)

        x1, y1, z1 = to_block(pos1)
        x2, y2, z2 = to_block(pos2)

        xmin, xmax = sorted((x1, x2))
        ymin, ymax = sorted((y1, y2))
        zmin, zmax = sorted((z1, z2))

        return xmin, xmax, ymin, ymax, zmin, zmax
    
    async def   listener_events(self, log: str):
        if 'INFO]:' not in log:
            return

        elif not self._waiting_block_request:
            return

        elif log.endswith('The target block is not a block entity'):
            self._requested_block_data = 'NOT_BLOCK_ENTITY'
            return

        elif 'has the following block data' in log:
            match = re.search(r"(.*?) has the following block data: (.*)", log)
            data = match.group(2)

            self._requested_block_data = data

    async def   get_block_data(self, x: int, y: int, z: int, dim: str, path: str | None = None):
        if self._waiting_block_request:
            raise RuntimeError("Ya existe una petición de block data en curso.")

        self._waiting_block_request = True
        self._requested_block_data = None

        cmd = f'execute in minecraft:{dim} run data get block {x} {y} {z}'
        if path:
            cmd += f' {path}'

        self.server.execute(cmd)

        max_iter = 1000
        while self._requested_block_data is None and max_iter:
            max_iter -= 1
            await asyncio.sleep(0.01)

        result = self._requested_block_data

        self._waiting_block_request = False
        self._requested_block_data = None

        return result

    async def   get_player_position(self, player: str):
        raw_pos = await self.server.get_data(player, 'Pos')
        raw_pos = raw_pos[raw_pos.find('[')+1 : raw_pos.find(']')].split(',')
        pos = tuple(float(x.strip()[:-1]) for x in raw_pos)

        raw_dim = await self.server.get_data(player, 'Dimension')
        dim = raw_dim.replace('"','').split(':')[1]

        return pos, dim
    
    async def   _scan_region_for_block_entities(self, name: str, dim: str, region_by_chunk: dict):
        filepath = os.path.join(self.reg_bkps_dir, f"{name}.csv")

        valid_blocks = []
        total_found = 0

        self.server.send_response("@a", f"§7Escaneando región... §8({dim})")

        for (chunk_x, chunk_z), blocks in region_by_chunk.items():

            # LOG de chunk
            self.server.send_response(
                "@a",
                f"§8→ Chunk §f({chunk_x}, {chunk_z}) §8[{len(blocks)} bloques]"
            )

            for (x, y, z) in blocks:
                data = await self.get_block_data(x, y, z, dim)

                if not data or data == 'NOT_BLOCK_ENTITY':
                    continue

                id_match = re.search(r'\bid:\s*"([^"]+)"', data)
                if not id_match:
                    id_match = re.search(
                        r'\bid:\s*([a-z0-9_]+:[a-z0-9_]+)\b',
                        data,
                        re.IGNORECASE
                    )

                if not id_match:
                    continue

                block_id = id_match.group(1).lower()

                if not (
                    block_id == "minecraft:chest" or
                    block_id == "minecraft:barrel" or
                    block_id.endswith("_shulker_box")
                ):
                    continue

                total_found += 1
                valid_blocks.append((dim, x, y, z, block_id))

                # LOG cuando encuentra
                self.server.send_response(
                    "@a",
                    f"§a✔§f {block_id} en §e{x} {y} {z}"
                )

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("dimension,x,y,z,block_type\n")
            for row in valid_blocks:
                f.write(",".join(map(str, row)) + "\n")

        self.server.send_response(
            "@a",
            f"§bEscaneo finalizado.§f Encontrados: §e{total_found}§f → §b{name}.csv"
        )

    def         disable_command_feedback (self):
        self.server.execute('gamerule sendCommandFeedback false')

    def         enable_command_feedback  (self):
        self.server.execute('gamerule sendCommandFeedback true')

    def         _summon_finder_helper(self, x: int, y: int, z: int, dimension: str):

        nbt = (
            '{'
            'BlockState:{Name:"minecraft:gray_stained_glass"},'
            'Glowing:1b,'
            'Invisible:1b,'
            'Invulnerable:1b,'
            'PersistenceRequired:1b,'
            'Silent:1b,'
            'NoGravity:1b,'
            'Time:1,'
            'DropItem:0b,'
            'HurtEntities:0b,'
            'Tags:["finder_helper"]'
            '}'
        )

        self.server.execute(
            f'execute in minecraft:{dimension} run '
            f'summon minecraft:falling_block {x} {y} {z} {nbt}'
        )

    def         _kill_finder_helper(self, dimension: str | None = None):
        if dimension:
            self.server.execute(
                f'execute in minecraft:{dimension} run '
                f'kill @e[tag=finder_helper]'
            )
        else:
            self.server.execute('kill @e[tag=finder_helper]')
    
    async def   _mark_found_locations(self, locations: list[tuple[str,int,int,int]]):
        """
        locations: [(dim, x, y, z), ...]
        """

        tag = "finder_found"

        # invocar marcadores
        for (dim, x, y, z) in locations:
            nbt = (
                '{'
                'BlockState:{Name:"minecraft:white_stained_glass"},'
                'Glowing:1b,'
                'Invisible:1b,'
                'Invulnerable:1b,'
                'PersistenceRequired:1b,'
                'Silent:1b,'
                'NoGravity:1b,'
                'Time:1,'
                'DropItem:0b,'
                'HurtEntities:0b,'
                f'Tags:["{tag}"]'
                '}'
            )

            self.server.execute(
                f'execute in minecraft:{dim} run '
                f'summon minecraft:falling_block {x+0.5} {y} {z+0.5} {nbt}'
            )

        # esperar 5 segundos
        await asyncio.sleep(5)

        # eliminar todos
        self.server.execute(f'kill @e[tag={tag}]')

    async def   _show_region_wireframe(self, xmin, xmax, ymin, ymax, zmin, zmax, dim: str):
        step = 0.5          # separación entre partículas (más chico = más denso)
        duration = 3.0      # segundos
        interval = 1.0      # cada cuánto “refrescar” el dibujo
        max_y = 320         # opcional: evita Y raras si te pasas de límites del mundo

        # centrar en el bloque para que las líneas se vean mejor
        def p(x, y, z):
            y = max(-64, min(max_y, y))
            self.server.execute(
                f'execute in minecraft:{dim} run '
                f'particle minecraft:end_rod {x:.2f} {y:.2f} {z:.2f} 0 0 0 0 1 force @a'
            )

        # genera puntos en un segmento 3D alineado a eje (solo varía un eje)
        def segment_x(y, z, x0, x1):
            if x1 < x0: x0, x1 = x1, x0
            n = int((x1 - x0) / step) + 1
            for i in range(n + 1):
                p(x0 + i * step, y, z)

        def segment_y(x, z, y0, y1):
            if y1 < y0: y0, y1 = y1, y0
            n = int((y1 - y0) / step) + 1
            for i in range(n + 1):
                p(x, y0 + i * step, z)

        def segment_z(x, y, z0, z1):
            if z1 < z0: z0, z1 = z1, z0
            n = int((z1 - z0) / step) + 1
            for i in range(n + 1):
                p(x, y, z0 + i * step)

        # usar esquinas en “borde” del cubo: +1 para que el wireframe quede por fuera del bloque final
        x0, x1 = xmin, xmax + 1
        y0, y1 = ymin, ymax + 1
        z0, z1 = zmin, zmax + 1

        t_end = duration
        while t_end > 0:

            # 4 aristas verticales
            for x in (x0, x1):
                for z in (z0, z1):
                    segment_y(x + 0.5, z + 0.5, y0 + 0.5, y1 + 0.5)

            # 4 aristas eje X (abajo y arriba)
            for y in (y0, y1):
                for z in (z0, z1):
                    segment_x(y + 0.5, z + 0.5, x0 + 0.5, x1 + 0.5)

            # 4 aristas eje Z (abajo y arriba)
            for y in (y0, y1):
                for x in (x0, x1):
                    segment_z(x + 0.5, y + 0.5, z0 + 0.5, z1 + 0.5)

            await asyncio.sleep(interval)
            t_end -= interval
    
    def         _load_place_csv(self, name: str):
        filepath = os.path.join(self.reg_bkps_dir, f"{name}.csv")
        if not os.path.exists(filepath):
            return None

        rows = []
        with open(filepath, "r", encoding="utf-8") as f:
            lines = [ln.strip() for ln in f.read().splitlines() if ln.strip()]

        if not lines:
            return rows

        # saltar header si existe
        start = 1 if lines[0].lower().startswith("dimension,") else 0

        for ln in lines[start:]:
            parts = ln.split(",")
            if len(parts) < 5:
                continue
            dim = parts[0].strip()
            x = int(parts[1].strip())
            y = int(parts[2].strip())
            z = int(parts[3].strip())
            block_type = parts[4].strip()
            rows.append((dim, x, y, z, block_type))

        return rows

    async def   _search_on_place(self, player: str, name: str, item: str):
        rows = self._load_place_csv(name)
        if rows is None:
            self.server.send_response(player, f"§c✖§f No existe el registro: §e{name}.csv")
            return

        # normalizar item: si no trae namespace, asumir minecraft:
        item_id = item.strip()
        if ":" not in item_id:
            item_id = f"minecraft:{item_id}"
        item_id = item_id.lower()

        # agrupar por (dim, chunk_x, chunk_z)
        by_chunk = {}
        for (dim, x, y, z, block_type) in rows:
            chunk_x = x // 16
            chunk_z = z // 16
            key = (dim, chunk_x, chunk_z)
            if key not in by_chunk:
                by_chunk[key] = []
            by_chunk[key].append((x, y, z, block_type))

        self.server.send_response(player, f"§7Buscando §f{item_id}§7 en §b{name}§7 ...")

        found = 0
        found_locations = []

        try:
            for (dim, chunk_x, chunk_z), blocks in by_chunk.items():

                # forzar carga del chunk usando un bloque representativo
                bx, by, bz, _ = blocks[0]
                self.server.execute(
                    f'execute in minecraft:{dim} run forceload add {bx} {bz}'
                )

                for (x, y, z, block_type) in blocks:

                    # marcador en el bloque que se está analizando
                    self._kill_finder_helper(dim)
                    self._summon_finder_helper(x + 0.5, y, z + 0.5, dim)

                    # pedir inventario (Items)
                    data = await self.get_block_data(x, y, z, dim, path="Items")

                    if not data or data == 'NOT_BLOCK_ENTITY':
                        continue
                    
                    # búsqueda simple por id del item dentro del NBT
                    # (el NBT suele contener id:"minecraft:xxx")
                    if f'id: "{item_id}"' in data.lower():
                        found += 1
                        found_locations.append((dim, x, y, z))

                # quitar forceload del chunk
                self.server.execute(
                    f'execute in minecraft:{dim} run forceload remove {bx} {bz}'
                )

        finally:
            self._kill_finder_helper()

            if found_locations:
                asyncio.create_task(self._mark_found_locations(found_locations))

        self.server.send_response(
            player,
            f"§bBúsqueda finalizada.§f Coincidencias: §e{found}"
        )