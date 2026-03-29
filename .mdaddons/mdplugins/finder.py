import asyncio
import os
import math
import re
import struct
import time
import json
import csv
import urllib.request
import urllib.error
import unicodedata
from datetime import datetime

from Classes.AeServer import AeServer
from mcdis_rcon.utils import hover_and_suggest, extras

class mdplugin():
    def __init__(self, server: AeServer):
        self.server = server
        self.player_positions       = {}
        self.initial_default_place  = "MainStorage"
        self.last_find_query        = {}
        self.find_region_cache      = {}
        self.find_cache_ttl_seconds = 15 * 60
        self.minecraft_lang_version = "1.21.4"
        self.find_marker_cleanup_tasks = {}
        self.item_lang_index        = {
            'item_ids': set(),
            'by_en_name': {},
            'by_es_name': {},
        }
        self.scan_flash_duration_seconds = 10 * 60
        self.scan_flash_active      = set()
        self.last_scan_error_log    = {}
        self.max_region_blocks      = 10_000_000
        self.max_region_chunks      = 16 * 16

        self._rcon_host = '127.0.0.1'
        self._rcon_port = None
        self._rcon_password = None
        self._rcon_reader = None
        self._rcon_writer = None
        self._rcon_authed = False
        self._rcon_lock = asyncio.Lock()
        self._rcon_request_id = 1000
        self._scan_marker_seq = 0
        self.rcon_read_retries = 2
        self.rcon_retry_delay = 0.15
        
        for msg in (
            "The target block is not a block entity",
            "has the following block data",
            "Displaying particle minecraft:end⎽rod"
        ):
            if msg not in self.server.blacklist:
                self.server.blacklist.append(msg)

        self.reg_bkps_dir = os.path.join(self.server.path_plugins, 'finder')
        os.makedirs(self.reg_bkps_dir, exist_ok = True)
        self.meta_path = os.path.join(self.reg_bkps_dir, 'finder_meta.json')
        self.find_cache_path = os.path.join(self.reg_bkps_dir, 'finder_find_cache.json')
        self.lang_dir = os.path.join(self.reg_bkps_dir, 'lang')
        os.makedirs(self.lang_dir, exist_ok = True)
        safe_version = self.minecraft_lang_version.replace('.', '_')
        self.item_lang_csv_path = os.path.join(self.lang_dir, f'minecraft_item_lang_{safe_version}.csv')
        self.exclude_path = os.path.join(self.reg_bkps_dir, 'finder_excludes.json')
        self.scan_excluded_blocks = self._load_scan_excluded_blocks()
        self.places_meta = self._load_places_meta()
        self._load_rcon_settings()
        self._ensure_item_lang_csv()
        self._load_item_lang_index()
        self._load_find_region_cache()

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
            self.server.show_command(player, 'find <item>', 'Busca <item> en MainStorage.')
            self.server.show_command(player, 'fd help', 'Muestra los comandos del finder')

        elif self.server.is_command(message, 'fd help'):
            
            if not player in self.server.admins: return
            self.server.show_command(player, 'fd pos1', 'Establece la posición 1.')
            self.server.show_command(player, 'fd pos2', 'Establece la posición 2.')
            self.server.show_command(player, 'fd clear', 'Limpia pos1 y pos2.')
            self.server.show_command(player, 'fd list', 'Lista los lugares guardados.')
            self.server.show_command(player, 'fd scan <name> [-v]', 'Crea/actualiza un lugar. Con -v muestra flashes del scan.')
            self.server.show_command(player, 'fd check [<x> <y> <z> | opcional]', 'Verifica si un bloque entra como contenedor para scan.')
            self.server.show_command(player, 'fd toggle-block [<x> <y> <z> | opcional]', 'Alterna exclusión de bloque para que scan lo omita.')
            self.server.show_command(player, 'fd scan log', 'Muestra errores del ultimo scan.')
            self.server.show_command(player, 'fd scan clean', 'Limpia todos los flashes activos del scan.')
            self.server.show_command(player, 'fd remove <name>', 'Elimina el lugar guardado <name>.')
            self.server.show_command(player, 'fd ensure_csv', 'Verifica/crea el CSV de traducciones de ítems.')
            self.server.show_command(player, 'fd show_excludes', 'Muestra bloques excluidos durante 10 segundos.')

        elif self.server.is_command(message, 'find'):
            raw_query = message.removeprefix(f'{self.server.prefix}find').strip()
            if not raw_query:
                self.server.send_response(player, "§c✖§f Uso: find <item>")
                return
            raw_parts = raw_query.split()
            force_cache_refresh = '-f' in raw_parts
            if force_cache_refresh:
                raw_query = " ".join(part for part in raw_parts if part != '-f').strip()
                if not raw_query:
                    self.server.send_response(player, "§c✖§f Uso: find <item>")
                    return

            default_place = self.initial_default_place
            if not self._place_exists(default_place):
                self.server.send_response(
                    player,
                    f"§c✖§f El lugar por defecto no existe: §e{default_place}§f. Usa §ffd scan {default_place}"
                )
                return

            item_id = self._resolve_find_item_id(raw_query)
            if not item_id:
                self.server.send_response(player, f"§c✖§f Ítem no válido: §e{raw_query}")
                return

            await self._search_on_place(player, default_place, item_id, force_cache_refresh=force_cache_refresh)
            return

        elif not player in self.server.admins:
            return
        
        elif self.server.is_command(message, 'fd list'):
            self.show_places(player)
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

        elif self.server.is_command(message, 'fd check'):
            raw_args = message.removeprefix(f'{self.server.prefix}fd check').strip()
            args = raw_args.split() if raw_args else []

            if len(args) not in (0, 3):
                self.server.send_response(player, "§c✖§f Uso: fd check [x y z]")
                return

            pos, dim = await self.get_player_position(player)
            if len(args) == 3:
                try:
                    x = int(args[0])
                    y = int(args[1])
                    z = int(args[2])
                except ValueError:
                    self.server.send_response(player, "§c✖§f Coordenadas inválidas. Usa enteros: fd check <x> <y> <z>")
                    return
            else:
                x = math.floor(pos[0])
                y = math.floor(pos[1]) - 1
                z = math.floor(pos[2])

            inspect = await self._inspect_container_candidate(dim, x, y, z)

            if inspect.get('ok'):
                self.server.send_response(
                    player,
                    f"§a✔§f fd check §7[{dim} {x} {y} {z}]§f: entra como contenedor (§e{inspect.get('block_id')}§f)."
                )
                asyncio.create_task(self._flash_check_location(dim, x, y, z, block_name="minecraft:lime_stained_glass"))
            else:
                reason = inspect.get('reason', 'No pasó criterio.')
                block_id = inspect.get('block_id')
                if block_id:
                    reason = f"{reason} ID detectado: {block_id}"
                self.server.send_response(
                    player,
                    f"§c✖§f fd check §7[{dim} {x} {y} {z}]§f: {reason}"
                )
                asyncio.create_task(self._flash_check_location(dim, x, y, z, block_name="minecraft:red_stained_glass"))
            return

        elif self.server.is_command(message, 'fd toggle-block'):
            raw_args = message.removeprefix(f'{self.server.prefix}fd toggle-block').strip()
            args = raw_args.split() if raw_args else []

            if len(args) not in (0, 3):
                self.server.send_response(player, "§c✖§f Uso: fd toggle-block [x y z]")
                return

            pos, dim = await self.get_player_position(player)
            if len(args) == 3:
                try:
                    x = int(args[0])
                    y = int(args[1])
                    z = int(args[2])
                except ValueError:
                    self.server.send_response(player, "§c✖§f Coordenadas inválidas. Usa enteros: fd toggle-block <x> <y> <z>")
                    return
            else:
                x = math.floor(pos[0])
                y = math.floor(pos[1]) - 1
                z = math.floor(pos[2])

            was_excluded = self._is_scan_block_excluded(dim, x, y, z)
            self._set_scan_block_excluded(dim, x, y, z, excluded=(not was_excluded))

            if was_excluded:
                self.server.send_response(player, f"§a✔§f Bloque removido de exclusión: §7[{dim} {x} {y} {z}]")
                asyncio.create_task(
                    self._flash_toggle_block_location_falling(
                        dim,
                        x,
                        y,
                        z,
                        block_name="minecraft:lime_stained_glass",
                        duration=2.0
                    )
                )
            else:
                self.server.send_response(player, f"§e✔§f Bloque excluido de scan: §7[{dim} {x} {y} {z}]")
                asyncio.create_task(
                    self._flash_toggle_block_location_falling(
                        dim,
                        x,
                        y,
                        z,
                        block_name="minecraft:red_stained_glass",
                        duration=2.0
                    )
                )
            return

        elif self.server.is_command(message, 'fd show_excludes'):
            await self._show_excluded_blocks_markers(player, duration=10.0)
            return

        elif self.server.is_command(message, 'fd ensure_csv'):
            force_rebuild = message.removeprefix(f'{self.server.prefix}fd ensure_csv').strip().lower() in ('-f', '--force')
            if force_rebuild and os.path.exists(self.item_lang_csv_path):
                try:
                    os.remove(self.item_lang_csv_path)
                except Exception as e:
                    self.server.send_response(player, f"§c✖§f No se pudo recrear CSV: §7{e}")
                    return
            status = self._ensure_item_lang_csv()
            code = status.get('status')
            version_note = f" §8| Versión: §f{self.minecraft_lang_version}"
            if code == 'exists':
                size_note = ""
                try:
                    size_note = f" §8| Peso: §f{self._format_size(os.path.getsize(self.item_lang_csv_path))}"
                except Exception:
                    pass
                self.server.send_response(player, f"§7CSV ya existe: §f{self.item_lang_csv_path}{size_note}{version_note}")
            elif code == 'created':
                self._load_item_lang_index()
                en_source = status.get('en_source', 'en_us')
                source_note = f" §8| EN: §f{en_source}" if en_source else ""
                size_note = ""
                try:
                    size_note = f" §8| Peso: §f{self._format_size(os.path.getsize(self.item_lang_csv_path))}"
                except Exception:
                    pass
                self.server.send_response(
                    player,
                    f"§a✔§f CSV creado: §f{self.item_lang_csv_path} §8| Filas: §f{status.get('rows', 0)}{size_note}{source_note}{version_note}"
                )
                downloaded = status.get('downloaded_langs', [])
                if downloaded:
                    self.server.send_response(player, f"§8[Finder] Descargados OK: §f{', '.join(downloaded)}")
            elif code == 'missing_en_us':
                self.server.send_response(player, f"§c✖§f No se pudo crear CSV: no se pudo descargar §een_us§f.{version_note}")
            elif code == 'download_errors':
                missing = ", ".join(status.get('missing_langs', []))
                self.server.send_response(
                    player,
                    f"§c✖§f No se pudo crear CSV. Faltan langs: §e{missing}{version_note}"
                )
                downloaded = status.get('downloaded_langs', [])
                if downloaded:
                    self.server.send_response(player, f"§8[Finder] Descargados OK: §f{', '.join(downloaded)}")
                errors = status.get('errors', [])
                if errors:
                    self.server.send_response(player, "§8[Finder] Errores de acceso:")
                    for err in errors:
                        self.server.send_response(player, f"§7- {err}")
            elif code == 'no_items':
                self.server.send_response(player, "§c✖§f No se pudo crear CSV: no se encontraron claves §eitem.minecraft.*§f.")
            elif code == 'write_error':
                self.server.send_response(player, f"§c✖§f Error escribiendo CSV: §7{status.get('error', 'desconocido')}")
            else:
                self.server.send_response(player, "§c✖§f No se pudo crear/verificar el CSV.")
            return

        elif self.server.is_command(message, 'fd scan clean'):
            await self._clean_scan_flash_markers(player)
            return

        elif self.server.is_command(message, 'fd scan log'):
            self._show_last_scan_error_log(player)
            return
            
        elif self.server.is_command(message, 'fd scan'):
            args = message.removeprefix(f'{self.server.prefix}fd scan').strip().split()
            verbose_scan = False
            test_mode = False
            name_parts = []

            for arg in args:
                opt = arg.lower()
                if opt == '-v':
                    verbose_scan = True
                elif opt == '-t':
                    test_mode = True
                else:
                    name_parts.append(arg)

            if len(name_parts) > 1:
                self.server.send_response(player, "§c✖§f Uso: fd scan <name> [-v] [-t]  |  fd scan -t [-v]")
                return

            name = name_parts[0].strip() if name_parts else ""
            if not name and not test_mode:
                self.server.send_response(player, "§c✖§f Uso: fd scan <name> [-v] [-t]")
                return

            # cada scan inicia limpio para evitar mezclar flashes antiguos
            await self._clean_scan_flash_markers()
            await self._upsert_place(player, name, verbose_scan=verbose_scan, test_mode=test_mode)
            return

        elif self.server.is_command(message, 'fd remove'):
            name = message.removeprefix(f'{self.server.prefix}fd remove').strip().replace(" ", "")
            if name.endswith('.csv'):
                name = name.removesuffix('.csv')

            if not name:
                self.server.send_response(player, "✖ Debes proveer un nombre.")
                return

            filepath = os.path.join(self.reg_bkps_dir, f"{name}.csv")
            if not os.path.exists(filepath):
                self.server.send_response(player, f"✖ No existe el lugar guardado: {name}")
                return

            os.remove(filepath)
            if name in self.places_meta:
                self.places_meta.pop(name, None)
                self._save_places_meta()
            if name in self.find_region_cache:
                self.find_region_cache.pop(name, None)
                self._save_find_region_cache()
            self.server.send_response(player, f"✔ Lugar eliminado: {name}")
            self.show_places(player)

    async def   _upsert_place(
        self,
        player: str,
        name: str,
        verbose_scan: bool = False,
        test_mode: bool = False
    ):
        name = (name or "").strip()
        if name.endswith('.csv'):
            name = name.removesuffix('.csv')

        if not name and not test_mode:
            self.server.send_response(player, "§c✖§f Debes indicar un nombre de lugar.")
            return

        rcon_ready, rcon_error = await self._ensure_rcon_ready()
        if not rcon_ready:
            self.server.send_response(player, f"§c✖§f {rcon_error}")
            return

        place_exists = self._place_exists(name) if name else False
        meta = self.places_meta.get(name) if name else None
        use_meta_region = place_exists and isinstance(meta, dict)

        if use_meta_region:
            dim = meta.get('dimension')
            pos1 = tuple(meta.get('pos1', []))
            pos2 = tuple(meta.get('pos2', []))

            if len(pos1) != 3 or len(pos2) != 3 or not dim:
                self.server.send_response(player, f"§c✖§f Metadatos inválidos para el lugar: §e{name}")
                return
        else:
            _, dim = await self.get_player_position(player)
            pos1 = self.player_positions[player][dim]['pos1']
            pos2 = self.player_positions[player][dim]['pos2']

            if pos1 is None or pos2 is None:
                self.server.send_response(player, "✖ Debes establecer pos1 y pos2 en esta dimensión.")
                return

        xmin, xmax, ymin, ymax, zmin, zmax = self._region_bounds(pos1, pos2)
        total_blocks = (xmax - xmin + 1) * (ymax - ymin + 1) * (zmax - zmin + 1)
        total_chunks = self._region_chunk_count(xmin, xmax, zmin, zmax)

        if total_chunks > self.max_region_chunks:
            self.server.send_response(
                player,
                f"✖ Región demasiado grande ({total_chunks} chunks). Límite: {self.max_region_chunks} (16x16)."
            )
            return

        if total_blocks > self.max_region_blocks:
            self.server.send_response(
                player,
                f"✖ Región demasiado grande ({total_blocks} bloques). Límite: {self.max_region_blocks}."
            )
            return

        region_by_chunk = self._build_region_by_chunk(xmin, xmax, ymin, ymax, zmin, zmax)
        scan_ok = await self._scan_region_for_block_entities(
            player,
            name,
            dim,
            region_by_chunk,
            verbose_scan=verbose_scan,
            save_results=(not test_mode)
        )
        if not scan_ok:
            return

        if test_mode:
            return

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        created_at = meta.get('created_at') if isinstance(meta, dict) and meta.get('created_at') else now
        self.places_meta[name] = {
            'dimension': dim,
            'pos1': list(pos1),
            'pos2': list(pos2),
            'created_at': created_at,
            'updated_at': now,
        }
        self._save_places_meta()

        if place_exists:
            self.server.send_response(player, f"§a✔§f Lugar actualizado: §b{name}")
        else:
            self.server.send_response(player, f"§a✔§f Lugar creado: §b{name}")
    
    async def   _send_region_size_feedback(self, player: str, dim, pos1, pos2):
        xmin, xmax, ymin, ymax, zmin, zmax = self._region_bounds(pos1, pos2)
        asyncio.create_task(
            self._show_region_wireframe(xmin, xmax, ymin, ymax, zmin, zmax, dim)
        )

        total_blocks = (xmax - xmin + 1) * (ymax - ymin + 1) * (zmax - zmin + 1)
        total_chunks = self._region_chunk_count(xmin, xmax, zmin, zmax)

        if total_chunks > self.max_region_chunks:
            self.server.send_response(
                player,
                f"§e⚠§f Región: §e{total_chunks}§f chunks. Límite: §e{self.max_region_chunks}§f (16x16)."
            )
        elif total_blocks > self.max_region_blocks:
            self.server.send_response(
                player,
                f"§e⚠§f Región: §e{total_blocks}§f bloques. Límite: §e{self.max_region_blocks}§f."
            )
        else:
            self.server.send_response(
                player,
                f"§7Región: §f{total_blocks}§7 bloques, §f{total_chunks}§7 chunks."
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

    def         _region_chunk_count(self, xmin: int, xmax: int, zmin: int, zmax: int):
        min_chunk_x = xmin // 16
        max_chunk_x = xmax // 16
        min_chunk_z = zmin // 16
        max_chunk_z = zmax // 16
        chunks_x = (max_chunk_x - min_chunk_x) + 1
        chunks_z = (max_chunk_z - min_chunk_z) + 1
        return chunks_x * chunks_z
    
    async def   get_block_data(self, x: int, y: int, z: int, dim: str, path: str | None = None):
        cmd = f'execute in minecraft:{dim} run data get block {x} {y} {z}'
        if path:
            cmd += f' {path}'

        return await self._get_block_data_by_rcon(cmd)

    async def   _get_block_data_with_retries(
        self,
        x: int,
        y: int,
        z: int,
        dim: str,
        path: str | None = None,
        retries: int | None = None
    ):
        max_retries = self.rcon_read_retries if retries is None else max(0, retries)
        attempt = 0
        last_error = None

        while attempt <= max_retries:
            try:
                return await self.get_block_data(x, y, z, dim, path)
            except Exception as e:
                last_error = e
                try:
                    await self._close_rcon()
                except Exception:
                    pass
                if attempt >= max_retries:
                    break
                await asyncio.sleep(self.rcon_retry_delay)
                attempt += 1

        raise RuntimeError(f"{last_error}")

    def         _load_places_meta(self):
        if not os.path.exists(self.meta_path):
            return {}

        try:
            with open(self.meta_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, dict):
                return data
        except Exception:
            pass

        return {}

    def         _save_places_meta(self):
        try:
            with open(self.meta_path, 'w', encoding='utf-8') as f:
                json.dump(self.places_meta, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def         _exclude_block_key(self, dim: str, x: int, y: int, z: int):
        return f"{dim}|{int(x)}|{int(y)}|{int(z)}"

    def         _load_scan_excluded_blocks(self):
        if not os.path.exists(self.exclude_path):
            return set()
        try:
            with open(self.exclude_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, list):
                return set(str(x) for x in data)
        except Exception:
            pass
        return set()

    def         _save_scan_excluded_blocks(self):
        try:
            with open(self.exclude_path, 'w', encoding='utf-8') as f:
                json.dump(sorted(self.scan_excluded_blocks), f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def         _is_scan_block_excluded(self, dim: str, x: int, y: int, z: int):
        key = self._exclude_block_key(dim, x, y, z)
        return key in self.scan_excluded_blocks

    def         _set_scan_block_excluded(self, dim: str, x: int, y: int, z: int, excluded: bool):
        key = self._exclude_block_key(dim, x, y, z)
        if excluded:
            self.scan_excluded_blocks.add(key)
        else:
            self.scan_excluded_blocks.discard(key)
        self._save_scan_excluded_blocks()

    def         _download_lang_json(self, lang_code: str):
        version = self.minecraft_lang_version
        urls = [
            f"https://mcasset.cloud/{version}/assets/minecraft/lang/{lang_code}.json",
            f"https://raw.githubusercontent.com/misode/mcmeta/{version}-assets/assets/minecraft/lang/{lang_code}.json",
            f"https://raw.githubusercontent.com/misode/mcmeta/{version}-summary/assets/minecraft/lang/{lang_code}.json",
            f"https://raw.githubusercontent.com/tunwinaung742/Minecraft-All-Lang/main/{lang_code}.json",
            f"https://raw.githubusercontent.com/toxicity188/all-minecraft-language/main/{lang_code}.json",
        ]

        errors = []
        for url in urls:
            try:
                with urllib.request.urlopen(url, timeout=10) as response:
                    if response.status != 200:
                        errors.append(f"{lang_code} -> {url} [HTTP {response.status}]")
                        continue
                    payload = response.read().decode('utf-8')
                data = json.loads(payload)
                if isinstance(data, dict):
                    return data, []
                errors.append(f"{lang_code} -> {url} [JSON inválido]")
            except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError, UnicodeDecodeError) as e:
                errors.append(f"{lang_code} -> {url} [{type(e).__name__}]")
            except Exception as e:
                errors.append(f"{lang_code} -> {url} [{type(e).__name__}]")
                continue

        return None, errors

    def         _ensure_item_lang_csv(self):
        # crear solo si falta; no regenerar en cada inicio
        if os.path.exists(self.item_lang_csv_path):
            return {'status': 'exists'}

        lang_priority = ['en_us', 'es_es', 'es_mx', 'es_ar', 'es_cl', 'es_ec', 'es_uy', 'es_ve']
        lang_data = {}
        download_errors = []
        downloaded_langs = []

        for lang_code in lang_priority:
            data, errors = self._download_lang_json(lang_code)
            if isinstance(data, dict):
                lang_data[lang_code] = data
                downloaded_langs.append(lang_code)
            if errors:
                download_errors.extend(errors)

        # verificar todos los langs antes de crear el csv
        missing_langs = [x for x in lang_priority if x not in lang_data]
        if missing_langs:
            return {
                'status': 'download_errors',
                'errors': download_errors,
                'missing_langs': missing_langs,
                'downloaded_langs': downloaded_langs,
            }

        en_us = lang_data.get('en_us')
        if not isinstance(en_us, dict):
            return {'status': 'missing_en_us'}

        item_ids = []
        for key in en_us.keys():
            if not isinstance(key, str):
                continue
            if key.startswith('item.minecraft.'):
                item_ids.append('minecraft:' + key.removeprefix('item.minecraft.'))
                continue
            if not key.startswith('block.minecraft.'):
                continue
            item_ids.append('minecraft:' + key.removeprefix('block.minecraft.'))
        item_ids = sorted(set(item_ids))

        if not item_ids:
            return {'status': 'no_items'}

        headers = ['item_id', 'en_us'] + [x for x in lang_priority if x != 'en_us']

        try:
            with open(self.item_lang_csv_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(headers)

                for item_id in item_ids:
                    suffix = item_id.removeprefix('minecraft:')
                    item_key = 'item.minecraft.' + suffix
                    block_key = 'block.minecraft.' + suffix
                    row = [item_id]
                    row.append(str(en_us.get(item_key, en_us.get(block_key, '')) or ''))

                    for lang_code in headers[2:]:
                        lang_dict = lang_data.get(lang_code, {})
                        if isinstance(lang_dict, dict):
                            text = lang_dict.get(item_key, lang_dict.get(block_key, ''))
                        else:
                            text = ''
                        row.append(str(text or ''))
                    writer.writerow(row)
            return {
                'status': 'created',
                'rows': len(item_ids),
                'en_source': 'en_us',
                'downloaded_langs': downloaded_langs,
            }
        except Exception as e:
            # no detener el plugin si falla creación de csv
            return {'status': 'write_error', 'error': str(e)}

    def         _normalize_find_text(self, text: str):
        raw = (text or "").strip().lower()
        raw = unicodedata.normalize('NFKD', raw)
        raw = ''.join(ch for ch in raw if not unicodedata.combining(ch))
        raw = re.sub(r'\s+', ' ', raw).strip()
        return raw

    def         _load_item_lang_index(self):
        index = {
            'item_ids': set(),
            'by_en_name': {},
            'by_es_name': {},
        }

        if not os.path.exists(self.item_lang_csv_path):
            self.item_lang_index = index
            return

        try:
            with open(self.item_lang_csv_path, 'r', encoding='utf-8-sig', newline='') as f:
                reader = csv.DictReader(f)
                if not reader.fieldnames:
                    self.item_lang_index = index
                    return

                fieldnames = [str(x).strip().lstrip('\ufeff') for x in reader.fieldnames]
                es_columns = [x for x in fieldnames if x.startswith('es_')]

                for row in reader:
                    normalized_row = {}
                    for k, v in row.items():
                        nk = str(k).strip().lstrip('\ufeff')
                        normalized_row[nk] = v

                    item_id = (normalized_row.get('item_id') or '').strip().lower()
                    if not item_id:
                        continue
                    index['item_ids'].add(item_id)

                    en_name = self._normalize_find_text(normalized_row.get('en_us') or '')
                    if en_name and en_name not in index['by_en_name']:
                        index['by_en_name'][en_name] = item_id

                    for col in es_columns:
                        es_name = self._normalize_find_text(normalized_row.get(col) or '')
                        if es_name and es_name not in index['by_es_name']:
                            index['by_es_name'][es_name] = item_id
        except Exception:
            pass

        self.item_lang_index = index

    def         _resolve_find_item_id(self, raw_query: str):
        query = self._normalize_find_text(raw_query)
        if not query:
            return None

        item_ids = self.item_lang_index.get('item_ids', set())
        if not item_ids and os.path.exists(self.item_lang_csv_path):
            self._load_item_lang_index()
            item_ids = self.item_lang_index.get('item_ids', set())
        if not item_ids:
            # fallback si no hay índice cargado
            candidate = query if query.startswith('minecraft:') else f"minecraft:{query.replace(' ', '_')}"
            candidate = candidate.lower()
            return candidate if re.fullmatch(r'minecraft:[a-z0-9_]+', candidate) else None

        if query.startswith('minecraft:'):
            candidate = query
            if re.fullmatch(r'minecraft:[a-z0-9_]+', candidate) and candidate in item_ids:
                return candidate
            return None

        # formato técnico (ej. golden_apple)
        if '_' in query or re.fullmatch(r'[a-z0-9_]+', query):
            candidate = f"minecraft:{query}"
            if candidate in item_ids:
                return candidate

        # intento directo por nombre inglés normalizado (con espacios)
        en_match = self.item_lang_index.get('by_en_name', {}).get(query)
        if en_match:
            return en_match

        # intento por nombre español normalizado
        es_match = self.item_lang_index.get('by_es_name', {}).get(query)
        if es_match:
            return es_match

        # fallback final: espacios -> _
        candidate = f"minecraft:{query.replace(' ', '_')}"
        if candidate in item_ids:
            return candidate

        return None

    def         _load_find_region_cache(self):
        if not os.path.exists(self.find_cache_path):
            self.find_region_cache = {}
            return

        try:
            with open(self.find_cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if not isinstance(data, dict):
                self.find_region_cache = {}
                return

            now_ts = time.time()
            restored = {}
            for name, entry in data.items():
                if not isinstance(entry, dict):
                    continue
                scanned_at = entry.get('scanned_at', 0)
                if not isinstance(scanned_at, (int, float)):
                    continue
                if (now_ts - scanned_at) > self.find_cache_ttl_seconds:
                    continue
                restored[name] = entry

            self.find_region_cache = restored
        except Exception:
            self.find_region_cache = {}

    def         _save_find_region_cache(self):
        try:
            with open(self.find_cache_path, 'w', encoding='utf-8') as f:
                json.dump(self.find_region_cache, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def         _format_size(self, size_bytes: int):
        units = ["B", "KB", "MB", "GB"]
        value = float(max(0, size_bytes))
        for unit in units:
            if value < 1024 or unit == units[-1]:
                if unit == "B":
                    return f"{int(value)} {unit}"
                return f"{value:.2f} {unit}"
            value /= 1024

    def         _load_rcon_settings(self):
        path = os.path.join(self.server.path_files, 'server', 'server.properties')
        if not os.path.exists(path):
            return

        props = {}
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            for ln in f:
                ln = ln.strip()
                if not ln or ln.startswith('#') or '=' not in ln:
                    continue
                key, value = ln.split('=', 1)
                props[key.strip()] = value.strip()

        if 'rcon.port' in props:
            try:
                self._rcon_port = int(props['rcon.port'])
            except ValueError:
                pass

        if 'rcon.password' in props:
            self._rcon_password = props['rcon.password']

        if 'rcon.ip' in props and props['rcon.ip']:
            self._rcon_host = props['rcon.ip']

    async def   _get_block_data_by_rcon(self, command: str):
        if self._rcon_port is None or not self._rcon_password:
            raise RuntimeError('No hay RCON conectado.')

        async with self._rcon_lock:
            response = await self._rcon_command(command)

        if 'The target block is not a block entity' in response:
            return 'NOT_BLOCK_ENTITY'

        match = re.search(r'has the following block data:\s*(.*)$', response, re.DOTALL)
        if match:
            return match.group(1).strip()

        return response.strip() or None

    async def   _ensure_rcon_ready(self):
        if self._rcon_port is None or not self._rcon_password:
            return False, 'No hay RCON conectado.'

        async with self._rcon_lock:
            try:
                await self._ensure_rcon_connection()
                return True, ''
            except Exception:
                await self._close_rcon()
                return False, 'No hay RCON conectado.'

    async def   _rcon_command(self, command: str):
        await self._ensure_rcon_connection()

        self._rcon_request_id += 1
        req_id = self._rcon_request_id

        await self._rcon_send_packet(req_id, 2, command)
        body = await self._rcon_read_response(req_id)

        return body

    async def   _ensure_rcon_connection(self):
        if self._rcon_writer is not None and not self._rcon_writer.is_closing() and self._rcon_authed:
            return

        self._rcon_reader, self._rcon_writer = await asyncio.wait_for(
            asyncio.open_connection(self._rcon_host, self._rcon_port),
            timeout = 2.0
        )
        self._rcon_authed = False

        self._rcon_request_id += 1
        req_id = self._rcon_request_id
        await self._rcon_send_packet(req_id, 3, self._rcon_password)

        auth_id = None
        for _ in range(2):
            packet_id, packet_type, _ = await self._rcon_read_packet()
            if packet_type == 2:
                auth_id = packet_id
                break
            auth_id = packet_id

        if auth_id != req_id:
            await self._close_rcon()
            raise RuntimeError('RCON auth failed')

        self._rcon_authed = True

    async def   _rcon_send_packet(self, packet_id: int, packet_type: int, body: str):
        if self._rcon_writer is None:
            raise RuntimeError('RCON socket not connected')

        body_bytes = body.encode('utf-8')
        payload = struct.pack('<ii', packet_id, packet_type) + body_bytes + b'\x00\x00'
        packet = struct.pack('<i', len(payload)) + payload

        self._rcon_writer.write(packet)
        await self._rcon_writer.drain()

    async def   _rcon_read_packet(self):
        if self._rcon_reader is None:
            raise RuntimeError('RCON socket not connected')

        length_raw = await asyncio.wait_for(self._rcon_reader.readexactly(4), timeout = 2.0)
        length = struct.unpack('<i', length_raw)[0]
        data = await asyncio.wait_for(self._rcon_reader.readexactly(length), timeout = 2.0)

        packet_id, packet_type = struct.unpack('<ii', data[:8])
        body = data[8:-2].decode('utf-8', errors='replace')

        return packet_id, packet_type, body

    async def   _rcon_read_response(self, expected_id: int):
        chunks = []
        for _ in range(10):
            packet_id, _, body = await self._rcon_read_packet()
            if packet_id != expected_id:
                continue
            chunks.append(body)
            if len(body) == 0:
                break
            if len(body) < 4096:
                break

        return ''.join(chunks)

    async def   _close_rcon(self):
        if self._rcon_writer is not None:
            try:
                self._rcon_writer.close()
                await self._rcon_writer.wait_closed()
            except Exception:
                pass

        self._rcon_reader = None
        self._rcon_writer = None
        self._rcon_authed = False

    async def   get_player_position(self, player: str):
        raw_pos = await self.server.get_data(player, 'Pos')
        raw_pos = raw_pos[raw_pos.find('[')+1 : raw_pos.find(']')].split(',')
        pos = tuple(float(x.strip()[:-1]) for x in raw_pos)

        raw_dim = await self.server.get_data(player, 'Dimension')
        dim = raw_dim.replace('"','').split(':')[1]

        return pos, dim

    def         _normalize_block_entity_id(self, raw_id: str | None):
        if not raw_id:
            return None
        value = raw_id.strip().strip('"').lower()
        if ":" not in value and re.fullmatch(r"[a-z0-9_]+", value):
            value = f"minecraft:{value}"
        return value

    def         _is_supported_storage_block(self, block_id: str):
        return (
            block_id == "minecraft:chest" or
            block_id == "minecraft:barrel" or
            block_id == "minecraft:shulker_box" or
            block_id == "minecraft:dispenser" or
            block_id == "minecraft:dropper"
        )

    async def   _inspect_container_candidate(self, dim: str, x: int, y: int, z: int):
        try:
            block_id_raw = await self._get_block_data_with_retries(x, y, z, dim, path="id")
        except Exception as e:
            return {
                'ok': False,
                'reason': f'Error RCON: {e}',
                'block_id': None,
            }

        if not block_id_raw or block_id_raw == 'NOT_BLOCK_ENTITY':
            return {
                'ok': False,
                'reason': 'No es block entity.',
                'block_id': None,
            }

        block_id = self._normalize_block_entity_id(block_id_raw)
        if not block_id:
            return {
                'ok': False,
                'reason': 'No se pudo parsear el id de block entity.',
                'block_id': None,
            }

        if not self._is_supported_storage_block(block_id):
            return {
                'ok': False,
                'reason': 'Block entity no soportado para contenedor.',
                'block_id': block_id,
            }

        return {
            'ok': True,
            'reason': 'Contenedor válido para scan.',
            'block_id': block_id,
        }
    
    async def   _scan_region_for_block_entities(
        self,
        player: str,
        name: str,
        dim: str,
        region_by_chunk: dict,
        verbose_scan: bool = False,
        save_results: bool = True
    ):
        filepath = os.path.join(self.reg_bkps_dir, f"{name}.csv") if save_results and name else None

        valid_blocks = []
        total_found = 0
        found_by_type = {
            "minecraft:chest": 0,
            "minecraft:barrel": 0,
            "minecraft:shulker_box": 0,
            "minecraft:dispenser": 0,
            "minecraft:dropper": 0,
        }
        total_blocks = sum(len(blocks) for blocks in region_by_chunk.values())
        processed_blocks = 0
        started_at = time.perf_counter()
        last_progress_at = started_at
        scan_errors = 0
        last_scan_error = None
        scan_error_entries = []

        self.server.send_response(
            player,
            f"§7Escaneando §b{name}§7 en §f{dim}§7... §8({total_blocks} bloques)"
        )

        loaded_chunks = set()

        for (chunk_x, chunk_z) in region_by_chunk.keys():
            loaded_chunks.add((chunk_x, chunk_z))
            self.server.execute(
                f'execute in minecraft:{dim} run forceload add {chunk_x * 16} {chunk_z * 16}'
            )
        self.server.send_response(
            player,
            f"§8[Finder] Chunks cargados: §f{len(loaded_chunks)}§8 en §f{dim}§8. Esperando estabilización..."
        )
        await asyncio.sleep(1)

        try:
            for (_, _), blocks in region_by_chunk.items():
                for (x, y, z) in blocks:
                    if self._is_scan_block_excluded(dim, x, y, z):
                        processed_blocks += 1
                        now = time.perf_counter()
                        if total_blocks and (now - last_progress_at >= 2.0 or processed_blocks == total_blocks):
                            percent = (processed_blocks / total_blocks) * 100
                            self.server.send_response(
                                player,
                                f"§8[Finder] Progreso: §f{processed_blocks}/{total_blocks} §8({percent:.1f}%) §7| Encontrados: §e{total_found}"
                            )
                            last_progress_at = now
                        continue

                    inspect = await self._inspect_container_candidate(dim, x, y, z)
                    if str(inspect.get('reason', '')).startswith('Error RCON:'):
                        scan_errors += 1
                        last_scan_error = inspect.get('reason')
                        scan_error_entries.append((dim, x, y, z, inspect.get('reason')))
                        processed_blocks += 1
                        continue

                    processed_blocks += 1
                    if inspect.get('ok'):
                        total_found += 1
                        block_id = inspect.get('block_id')
                        valid_blocks.append((dim, x, y, z, block_id))
                        found_by_type[block_id] = found_by_type.get(block_id, 0) + 1
                        if verbose_scan:
                            await self._flash_scan_location(dim, x, y, z)

                    now = time.perf_counter()
                    if total_blocks and (now - last_progress_at >= 2.0 or processed_blocks == total_blocks):
                        percent = (processed_blocks / total_blocks) * 100
                        self.server.send_response(
                            player,
                            f"§8[Finder] Progreso: §f{processed_blocks}/{total_blocks} §8({percent:.1f}%) §7| Encontrados: §e{total_found}"
                        )
                        last_progress_at = now
        finally:
            for (chunk_x, chunk_z) in loaded_chunks:
                self.server.execute(
                    f'execute in minecraft:{dim} run forceload remove {chunk_x * 16} {chunk_z * 16}'
                )
            self.server.send_response(
                player,
                f"§8[Finder] Chunks descargados: §f{len(loaded_chunks)}§8 en §f{dim}"
            )

        if scan_errors:
            self.server.send_response(
                player,
                f"§e⚠§f Scan completado con §e{scan_errors}§f errores de lectura RCON. Último error: §7{last_scan_error}"
            )

        self.last_scan_error_log[player] = {
            'place': name,
            'dimension': dim,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'errors': list(scan_error_entries),
        }

        if save_results and filepath:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("dimension,x,y,z,block_type\n")
                for row in valid_blocks:
                    f.write(",".join(map(str, row)) + "\n")

        elapsed = time.perf_counter() - started_at

        place_label = name if name else "[TEST]"
        summary_target = "@a" if save_results else player
        self.server.send_response(
            summary_target,
            f"§bEscaneo finalizado.§f Encontrados: §e{total_found}§f → §b{place_label} §7| Duración: §f{self._format_duration(elapsed)}"
        )
        self.server.send_response(
            player,
            "§8[Finder] Detalle: "
            f"§fChest: §e{found_by_type.get('minecraft:chest', 0)}§8 | "
            f"§fBarrel: §e{found_by_type.get('minecraft:barrel', 0)}§8 | "
            f"§fShulker: §e{found_by_type.get('minecraft:shulker_box', 0)}§8 | "
            f"§fDispenser: §e{found_by_type.get('minecraft:dispenser', 0)}§8 | "
            f"§fDropper: §e{found_by_type.get('minecraft:dropper', 0)}"
        )
        if verbose_scan:
            actions = [
                '{"text":"Limpiar Flashes: ","color":"dark_gray"}',
                hover_and_suggest(
                    f'{self.server.prefix}fd scan clean',
                    color='white',
                    suggest=f'{self.server.prefix}fd scan clean',
                    hover='Limpiar flashes del scan'
                ),
                '{"text":"  Logs: ","color":"dark_gray"}',
                hover_and_suggest(
                    f'{self.server.prefix}fd scan log',
                    color='white',
                    suggest=f'{self.server.prefix}fd scan log',
                    hover='Mostrar coordenadas con error del ultimo scan'
                )
            ]
            self.server.execute(f'tellraw {player} {extras(actions)}')
        return True

    def         _format_duration(self, seconds: float):
        total = max(0, int(round(seconds)))
        hours, rem = divmod(total, 3600)
        minutes, secs = divmod(rem, 60)

        parts = []
        if hours:
            parts.append(f"{hours}h")
        if minutes:
            parts.append(f"{minutes}m")
        parts.append(f"{secs}s")

        return " ".join(parts)

    def         disable_command_feedback (self):
        self.server.execute('gamerule sendCommandFeedback false')

    def         enable_command_feedback  (self):
        self.server.execute('gamerule sendCommandFeedback true')

    def         _find_marker_tag_for_player(self, player: str):
        safe = re.sub(r'[^a-zA-Z0-9_]', '_', player)
        return f"finder_found_{safe}"

    def         _cancel_find_marker_cleanup_for_player(self, player: str):
        task = self.find_marker_cleanup_tasks.pop(player, None)
        if task and not task.done():
            task.cancel()

    def         _clear_find_markers_for_player(self, player: str):
        self._cancel_find_marker_cleanup_for_player(player)
        tag = self._find_marker_tag_for_player(player)
        self.server.execute(f'kill @e[tag={tag}]')

    async def   _mark_found_locations(self, player: str, locations: list[tuple[str,int,int,int]], duration: float = 10.0):
        """
        locations: [(dim, x, y, z), ...]
        """

        tag = self._find_marker_tag_for_player(player)
        loaded_chunks = set()
        should_kill_markers = True

        for (dim, x, _, z) in locations:
            chunk_x = x // 16
            chunk_z = z // 16
            key = (dim, chunk_x, chunk_z)
            if key in loaded_chunks:
                continue
            loaded_chunks.add(key)
            self.server.execute(
                f'execute in minecraft:{dim} run forceload add {chunk_x * 16} {chunk_z * 16}'
            )

        try:
            # invocar marcadores
            for (dim, x, y, z) in locations:
                nbt = (
                    '{'
                    'block_state:{Name:"minecraft:lime_stained_glass"},'
                    'transformation:{'
                    'left_rotation:[0f,0f,0f,1f],'
                    'right_rotation:[0f,0f,0f,1f],'
                    'scale:[1.0f,1.0f,1.0f],'
                    'translation:[0f,0f,0f]'
                    '},'
                    'Glowing:1b,'
                    'Invisible:1b,'
                    'Invulnerable:1b,'
                    'PersistenceRequired:1b,'
                    'Silent:1b,'
                    f'Tags:["{tag}"]'
                    '}'
                )

                self.server.execute(
                    f'execute in minecraft:{dim} run '
                    f'summon minecraft:block_display {x:.1f} {y:.1f} {z:.1f} {nbt}'
                )

            # mantener marcador casi 10 segundos
            await asyncio.sleep(duration)
        except asyncio.CancelledError:
            should_kill_markers = False
            raise
        finally:
            if should_kill_markers:
                for dim in {d for (d, _, _, _) in locations}:
                    self.server.execute(f'execute in minecraft:{dim} run kill @e[tag={tag}]')
            for (dim, chunk_x, chunk_z) in loaded_chunks:
                self.server.execute(
                    f'execute in minecraft:{dim} run forceload remove {chunk_x * 16} {chunk_z * 16}'
                )
            current_task = asyncio.current_task()
            if self.find_marker_cleanup_tasks.get(player) is current_task:
                self.find_marker_cleanup_tasks.pop(player, None)

    async def   _flash_scan_location(self, dim: str, x: int, y: int, z: int):
        self._scan_marker_seq += 1
        tag = f"finder_scan_found_{self._scan_marker_seq}"
        common_tag = "finder_scan_flash"

        nbt = (
            '{'
            'block_state:{Name:"minecraft:lime_stained_glass"},'
            'transformation:{'
            'left_rotation:[0f,0f,0f,1f],'
            'right_rotation:[0f,0f,0f,1f],'
            'scale:[1.0f,1.0f,1.0f],'
            'translation:[0f,0f,0f]'
            '},'
            'Invisible:1b,'
            'Invulnerable:1b,'
            'PersistenceRequired:1b,'
            'Silent:1b,'
            f'Tags:["{tag}","{common_tag}"]'
            '}'
        )

        self.server.execute(
            f'execute in minecraft:{dim} run '
            f'summon minecraft:block_display {x:.1f} {y:.1f} {z:.1f} {nbt}'
        )
        self.scan_flash_active.add((dim, tag))
        asyncio.create_task(
            self._cleanup_scan_flash_marker(dim, tag, self.scan_flash_duration_seconds)
        )

    async def   _flash_check_location(
        self,
        dim: str,
        x: int,
        y: int,
        z: int,
        block_name: str = "minecraft:lime_stained_glass",
        duration: float = 2.0
    ):
        self._scan_marker_seq += 1
        tag = f"finder_scan_check_{self._scan_marker_seq}"
        common_tag = "finder_scan_check"

        nbt = (
            '{'
            f'block_state:{{Name:"{block_name}"}},'
            'transformation:{'
            'left_rotation:[0f,0f,0f,1f],'
            'right_rotation:[0f,0f,0f,1f],'
            'scale:[1.0f,1.0f,1.0f],'
            'translation:[0f,0f,0f]'
            '},'
            'Invisible:1b,'
            'Invulnerable:1b,'
            'PersistenceRequired:1b,'
            'Silent:1b,'
            f'Tags:["{tag}","{common_tag}"]'
            '}'
        )

        self.server.execute(
            f'execute in minecraft:{dim} run '
            f'summon minecraft:block_display {x:.1f} {y:.1f} {z:.1f} {nbt}'
        )
        await asyncio.sleep(duration)
        self.server.execute(f'execute in minecraft:{dim} run kill @e[tag={tag}]')

    async def   _flash_toggle_block_location_falling(
        self,
        dim: str,
        x: int,
        y: int,
        z: int,
        block_name: str = "minecraft:red_stained_glass",
        duration: float = 2.0
    ):
        self._scan_marker_seq += 1
        tag = f"finder_toggle_block_{self._scan_marker_seq}"

        nbt = (
            '{'
            f'BlockState:{{Name:"{block_name}"}},'
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
            f'summon minecraft:falling_block {x+0.5:.1f} {y:.1f} {z+0.5:.1f} {nbt}'
        )
        await asyncio.sleep(duration)
        self.server.execute(f'execute in minecraft:{dim} run kill @e[tag={tag}]')

    async def   _show_excluded_blocks_markers(self, player: str, duration: float = 10.0):
        if not self.scan_excluded_blocks:
            self.server.send_response(player, "§7No hay bloques excluidos.")
            return

        parsed = []
        for key in self.scan_excluded_blocks:
            try:
                dim, sx, sy, sz = key.split('|')
                parsed.append((dim, int(sx), int(sy), int(sz)))
            except Exception:
                continue

        if not parsed:
            self.server.send_response(player, "§7No hay bloques excluidos válidos.")
            return

        self._scan_marker_seq += 1
        common_tag = f"finder_show_excludes_{self._scan_marker_seq}"

        by_dim = {}
        for dim, x, y, z in parsed:
            if dim not in by_dim:
                by_dim[dim] = []
            by_dim[dim].append((x, y, z))

        loaded_chunks = set()
        for dim, entries in by_dim.items():
            for x, _, z in entries:
                chunk_x = x // 16
                chunk_z = z // 16
                key = (dim, chunk_x, chunk_z)
                if key in loaded_chunks:
                    continue
                loaded_chunks.add(key)
                self.server.execute(
                    f'execute in minecraft:{dim} run forceload add {chunk_x * 16} {chunk_z * 16}'
                )

        try:
            for dim, entries in by_dim.items():
                for x, y, z in entries:
                    self._scan_marker_seq += 1
                    tag = f"finder_show_exclude_{self._scan_marker_seq}"
                    nbt = (
                        '{'
                        'BlockState:{Name:"minecraft:red_stained_glass"},'
                        'Glowing:1b,'
                        'Invisible:1b,'
                        'Invulnerable:1b,'
                        'PersistenceRequired:1b,'
                        'Silent:1b,'
                        'NoGravity:1b,'
                        'Time:1,'
                        'DropItem:0b,'
                        'HurtEntities:0b,'
                        f'Tags:["{tag}","{common_tag}"]'
                        '}'
                    )
                    self.server.execute(
                        f'execute in minecraft:{dim} run '
                        f'summon minecraft:falling_block {x+0.5:.1f} {y:.1f} {z+0.5:.1f} {nbt}'
                    )
            self.server.send_response(player, f"§8[Finder] Mostrando excluidos: §f{len(parsed)}")
            await asyncio.sleep(duration)
        finally:
            for dim in by_dim.keys():
                self.server.execute(f'execute in minecraft:{dim} run kill @e[tag={common_tag}]')
            for dim, chunk_x, chunk_z in loaded_chunks:
                self.server.execute(
                    f'execute in minecraft:{dim} run forceload remove {chunk_x * 16} {chunk_z * 16}'
                )

    async def   _cleanup_scan_flash_marker(self, dim: str, tag: str, delay_seconds: float):
        await asyncio.sleep(delay_seconds)
        self.server.execute(f'execute in minecraft:{dim} run kill @e[tag={tag}]')
        self.scan_flash_active.discard((dim, tag))

    async def   _clean_scan_flash_markers(self, player: str | None = None):
        removed = len(self.scan_flash_active)
        self.server.execute('kill @e[tag=finder_scan_flash]')
        self.scan_flash_active.clear()
        if player:
            self.server.send_response(player, f"§a✔§f Flashes limpiados: §e{removed}")

    def         _show_last_scan_error_log(self, player: str):
        log = self.last_scan_error_log.get(player)
        if not log:
            self.server.send_response(player, "§e⚠§f No hay log de scan reciente.")
            return

        errors = log.get('errors', [])
        if not errors:
            self.server.send_response(player, "§7Último scan sin errores de lectura.")
            return

        place = log.get('place', '?')
        dim = log.get('dimension', '?')
        timestamp = log.get('timestamp', '?')
        self.server.send_response(
            player,
            f"§8[Finder] Errores del último scan §7({timestamp}) §8| Lugar: §f{place} §8| Dim: §f{dim}"
        )
        for (_, x, y, z, error_msg) in errors:
            safe_error = str(error_msg).replace('\n', ' ').replace('\r', ' ')
            self.server.send_response(player, f"§f- §e{x} {y} {z}§8 -> §7{safe_error}")

    async def   _flash_find_analysis_location(self, dim: str, x: int, y: int, z: int, duration: float = 2.0):
        self._scan_marker_seq += 1
        tag = f"finder_scan_analysis_{self._scan_marker_seq}"
        common_tag = "finder_scan_analysis"

        nbt = (
            '{'
            'BlockState:{Name:"minecraft:white_stained_glass"},'
            'Glowing:1b,'
            'Invisible:0b,'
            'Invulnerable:1b,'
            'PersistenceRequired:1b,'
            'Silent:1b,'
            'NoGravity:1b,'
            'Time:1,'
            'DropItem:0b,'
            'HurtEntities:0b,'
            f'Tags:["{tag}","{common_tag}"]'
            '}'
        )

        self.server.execute(
            f'execute in minecraft:{dim} run '
            f'summon minecraft:falling_block {x+0.5} {y} {z+0.5} {nbt}'
        )
        await asyncio.sleep(duration)
        self.server.execute(f'execute in minecraft:{dim} run kill @e[tag={tag}]')

    def         _summon_finder_helper(self, x: int, y: int, z: int, dimension: str):
        nbt = (
            '{'
            'BlockState:{Name:"minecraft:gray_stained_glass"},'
            'Glowing:1b,'
            'Invisible:0b,'
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

        # usar aristas reales del cubo en coordenadas decimales explícitas
        x0, x1 = float(xmin), float(xmax + 1)
        y0, y1 = float(ymin), float(ymax + 1)
        z0, z1 = float(zmin), float(zmax + 1)

        t_end = duration
        while t_end > 0:

            # 4 aristas verticales
            for x in (x0, x1):
                for z in (z0, z1):
                    segment_y(x, z, y0, y1)

            # 4 aristas eje X (abajo y arriba)
            for y in (y0, y1):
                for z in (z0, z1):
                    segment_x(y, z, x0, x1)

            # 4 aristas eje Z (abajo y arriba)
            for y in (y0, y1):
                for x in (x0, x1):
                    segment_z(x, y, z0, z1)

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

    def         _place_exists(self, name: str):
        filepath = os.path.join(self.reg_bkps_dir, f"{name}.csv")
        return os.path.exists(filepath)

    def         _send_found_coordinates(self, player: str, locations: list[tuple[str, int, int, int]]):
        if not locations:
            return
        dim_colors = {
            'overworld': 'green',
            'minecraft:overworld': 'green',
            'the_nether': 'red',
            'minecraft:the_nether': 'red',
            'the_end': 'yellow',
            'minecraft:the_end': 'yellow',
        }
        dim_labels = {
            'overworld': 'Overworld',
            'minecraft:overworld': 'Overworld',
            'the_nether': 'Nether',
            'minecraft:the_nether': 'Nether',
            'the_end': 'End',
            'minecraft:the_end': 'End',
        }

        # self.server.send_response(player, "§7Contenedores:")
        # chunk_size = 3
        # for start in range(0, len(locations), chunk_size):
        #     chunk = locations[start:start + chunk_size]
        #     actions = ['{"text":"- ","color":"gray"}']

        #     for idx, (dim, x, y, z) in enumerate(chunk):
        #         color = dim_colors.get(dim, 'white')
        #         actions.append(
        #             hover(
        #                 f'[{x} {y} {z}]',
        #                 color=color,
        #                 hover=f"Dimensión: {dim_labels.get(dim, dim)}"
        #             )
        #         )
        #         if idx < len(chunk) - 1:
        #             actions.append('{"text":" ","color":"gray"}')

        #     self.server.execute(f'tellraw {player} {extras(actions)}')

    async def   _trace_paths_from_player_to_locations(
        self,
        player: str,
        locations: list[tuple[str, int, int, int]],
        origin_pos: tuple[float, float, float] | None = None,
        origin_dim: str | None = None,
        duration: float = 10.0,
        interval: float = 2.0,
        step: float = 1.0,
        max_paths: int = 20,
        max_distance: float = 128.0,
        max_refreshes: int = 4
    ):
        if not locations:
            return

        def distance(a: tuple[float, float, float], b: tuple[float, float, float]):
            dx = b[0] - a[0]
            dy = b[1] - a[1]
            dz = b[2] - a[2]
            return math.sqrt(dx * dx + dy * dy + dz * dz)

        filtered_locations = list(locations)
        if origin_pos is not None and origin_dim:
            ox, oy, oz = origin_pos
            tmp = []
            for (dim, x, y, z) in locations:
                if dim != origin_dim:
                    continue
                d = distance((ox, oy, oz), (x + 0.5, y + 0.5, z + 0.5))
                if d <= max_distance:
                    tmp.append((dim, x, y, z))
            filtered_locations = tmp

        if not filtered_locations:
            return

        def draw_line(dim: str, x1: float, y1: float, z1: float, x2: float, y2: float, z2: float):
            dx = x2 - x1
            dy = y2 - y1
            dz = z2 - z1
            dist = math.sqrt(dx * dx + dy * dy + dz * dz)
            if dist <= 0:
                return

            points = int(dist / step)
            if points <= 0:
                points = 1

            for i in range(points + 1):
                t = i / points
                px = x1 + (dx * t)
                py = y1 + (dy * t)
                pz = z1 + (dz * t)
                self.server.execute(
                    f'execute in minecraft:{dim} run '
                    f'particle minecraft:end_rod {px:.2f} {py:.2f} {pz:.2f} 0 0 0 0 1 force @a' #{player}
                )

        t_end = duration
        refresh_count = 0
        while t_end > 0 and refresh_count < max_refreshes:
            if origin_pos is None or not origin_dim:
                return

            same_dim_locations = [(d, x, y, z) for (d, x, y, z) in filtered_locations if d == origin_dim]
            same_dim_locations = same_dim_locations[:max_paths]

            px, py, pz = origin_pos
            for (_, x, y, z) in same_dim_locations:
                draw_line(origin_dim, px, py + 0.8, pz, x + 0.5, y + 0.8, z + 0.5)

            await asyncio.sleep(interval)
            t_end -= interval
            refresh_count += 1

    def         _build_region_by_chunk(self, xmin, xmax, ymin, ymax, zmin, zmax):
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

        return region_by_chunk

    def         show_places(self, player: str):
        places = [x for x in os.listdir(self.reg_bkps_dir) if x.endswith('.csv')]
        places.sort()

        if not places:
            self.server.send_response(player, 'No hay lugares guardados.')
            return

        self.server.send_response(player, 'Lugares guardados:')
        can_delete = player in self.server.admins
        default_place = self.initial_default_place

        for place in places:
            place_name = place.removesuffix('.csv')
            place_path = os.path.join(self.reg_bkps_dir, place)
            creation_time = datetime.fromtimestamp(os.path.getctime(place_path))

            actions = [
                hover_and_suggest(
                    '[⟳] ',
                    color='green',
                    suggest=f'{self.server.prefix}fd scan {place_name}',
                    hover='Actualizar lugar'
                ),
                hover_and_suggest(
                    '[?] ',
                    color='aqua',
                    suggest=f'{self.server.prefix}find ',
                    hover='Buscar item en MainStorage'
                )
            ]

            if can_delete:
                actions.append(
                    hover_and_suggest(
                        '[x] ',
                        color='red',
                        suggest=f'{self.server.prefix}fd remove {place_name}',
                        hover='Eliminar lugar'
                    )
                )

            label = place_name
            if place_name == default_place:
                label = f'{place_name} [DEFAULT]'
            if place_name not in self.places_meta:
                label = f'{label} [NO_META]'

            actions.append(
                f'{{"text":"{label} [{creation_time.strftime("%Y-%m-%d %H:%M:%S")}]"}}'
            )

            self.server.execute(f'tellraw {player} {extras(actions)}')

    async def   _search_on_place(self, player: str, name: str, item: str, force_cache_refresh: bool = False):
        rcon_ready, rcon_error = await self._ensure_rcon_ready()
        if not rcon_ready:
            self.server.send_response(player, f"§c✖§f {rcon_error}")
            return

        rows = self._load_place_csv(name)
        if rows is None:
            self.server.send_response(player, f"§c✖§f No existe el lugar: §e{name}")
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

        self.server.send_response(player, f"§7Buscando en §b{name} §7→ §f{item_id}")
        total_entries = len(rows)

        cache_path = os.path.join(self.reg_bkps_dir, f"{name}.csv")
        csv_mtime = os.path.getmtime(cache_path) if os.path.exists(cache_path) else None
        now_ts = time.time()
        cache_entry = self.find_region_cache.get(name)
        use_region_cache = (
            (not force_cache_refresh) and
            cache_entry is not None and
            (now_ts - cache_entry.get('scanned_at', 0)) <= self.find_cache_ttl_seconds and
            cache_entry.get('csv_mtime') == csv_mtime and
            cache_entry.get('rows_count') == len(rows)
        )

        inventories_snapshot = []
        if use_region_cache:
            inventories_snapshot = list(cache_entry.get('inventories', []))
            self.server.send_response(player, "§8[Finder] Usando caché.")
        else:
            if force_cache_refresh:
                self.server.send_response(player, "§8[Finder] Forzando recreación de caché...")
            loaded_chunks_by_dim = set()
            read_errors = 0
            processed_entries = 0
            last_progress_at = time.perf_counter()

            self.server.send_response(player, "§8[Finder] Creando caché de la región...")

            try:
                for (dim, chunk_x, chunk_z) in by_chunk.keys():
                    loaded_chunks_by_dim.add((dim, chunk_x, chunk_z))
                    self.server.execute(
                        f'execute in minecraft:{dim} run forceload add {chunk_x * 16} {chunk_z * 16}'
                    )
                await asyncio.sleep(1)

                for (dim, _, _), blocks in by_chunk.items():
                    for (x, y, z, block_type) in blocks:
                        # asyncio.create_task(self._flash_find_analysis_location(dim, x, y, z, duration=2.0))
                        try:
                            data = await self._get_block_data_with_retries(x, y, z, dim, path="Items")
                        except Exception:
                            read_errors += 1
                            processed_entries += 1
                            now = time.perf_counter()
                            if total_entries and (now - last_progress_at >= 2.0 or processed_entries == total_entries):
                                percent = (processed_entries / total_entries) * 100
                                self.server.send_response(
                                    '@a', # player
                                    f"§8[Finder] Progreso caché: §f{processed_entries}/{total_entries} §8({percent:.1f}%)"
                                )
                                last_progress_at = now
                            continue

                        if not data or data == 'NOT_BLOCK_ENTITY':
                            inventories_snapshot.append((dim, x, y, z, ""))
                            processed_entries += 1
                            now = time.perf_counter()
                            if total_entries and (now - last_progress_at >= 2.0 or processed_entries == total_entries):
                                percent = (processed_entries / total_entries) * 100
                                self.server.send_response(
                                    player,
                                    f"§8[Finder] Progreso caché: §f{processed_entries}/{total_entries} §8({percent:.1f}%)"
                                )
                                last_progress_at = now
                            continue

                        inventories_snapshot.append((dim, x, y, z, data.lower()))
                        processed_entries += 1
                        now = time.perf_counter()
                        if total_entries and (now - last_progress_at >= 2.0 or processed_entries == total_entries):
                            percent = (processed_entries / total_entries) * 100
                            self.server.send_response(
                                player,
                                f"§8[Finder] Progreso caché: §f{processed_entries}/{total_entries} §8({percent:.1f}%)"
                            )
                            last_progress_at = now
            finally:
                self.server.execute('kill @e[tag=finder_scan_analysis]')
                for (dim, chunk_x, chunk_z) in loaded_chunks_by_dim:
                    self.server.execute(
                        f'execute in minecraft:{dim} run forceload remove {chunk_x * 16} {chunk_z * 16}'
                    )

            if read_errors:
                self.server.send_response(
                    player,
                    "§e⚠§f La búsqueda terminó con algunos errores de lectura."
                )

            self.find_region_cache[name] = {
                'scanned_at': time.time(),
                'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'csv_mtime': csv_mtime,
                'rows_count': len(rows),
                'inventories': list(inventories_snapshot),
            }
            self._save_find_region_cache()
            try:
                cache_size = os.path.getsize(self.find_cache_path)
                self.server.send_response(
                    player,
                    f"§8[Finder] Caché lista. §7Archivo: §f{self._format_size(cache_size)}"
                )
            except Exception:
                self.server.send_response(player, "§8[Finder] Caché lista.")

        found_locations = []
        for (dim, x, y, z, data_lc) in inventories_snapshot:
            if not data_lc:
                continue
            if f'id: "{item_id}"' in data_lc:
                found_locations.append((dim, x, y, z))

        found = len(found_locations)
        if found_locations:
            self._clear_find_markers_for_player(player)
            marker_task = asyncio.create_task(self._mark_found_locations(player, found_locations))
            self.find_marker_cleanup_tasks[player] = marker_task
            try:
                origin_pos, origin_dim = await self.get_player_position(player)
            except Exception:
                origin_pos, origin_dim = None, None
            asyncio.create_task(
                self._trace_paths_from_player_to_locations(
                    player,
                    found_locations,
                    origin_pos=origin_pos,
                    origin_dim=origin_dim
                )
            )

        self.server.send_response(player, f"§bCoincidencias: §e{found}")
        self._send_found_coordinates(player, found_locations)
        self.last_find_query[player] = {
            'place': name,
            'item_id': item_id,
            'found': found,
            'found_locations': list(found_locations),
        }
