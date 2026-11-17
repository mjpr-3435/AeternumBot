"""Parser for Minecraft .litematic schematics.

Extracts sub-regions/sections, calculates blocks and volumes, and aggregates
material lists formatted for Minecraft carpet/litematica exports.
"""

from __future__ import annotations

import csv
import gzip
import io
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any

import nbtlib  # type: ignore[import-not-found]

AIR_BLOCKS = frozenset({'minecraft:air', 'minecraft:cave_air', 'minecraft:void_air'})


def format_item_name(namespaced_id: str) -> str:
    """Convert ``'minecraft:white_wool'`` into ``'White Wool'``."""
    raw = namespaced_id.split(':', 1)[-1]
    words = raw.replace('_', ' ').split()
    return ' '.join(word.capitalize() for word in words)


def natural_sort_key(text: str) -> list[int | str]:
    """Sort strings with embedded numbers naturally (e.g. A1, A2, ..., A10)."""
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r'(\d+)', text)]


def unpack_region_blocks(r_data: dict[str, Any]) -> Counter[str]:
    """Unpack 64-bit bit-packed BlockStates for a Litematica region."""
    size = r_data.get('Size')
    if not size:
        return Counter()

    dx = abs(int(size['x']))
    dy = abs(int(size['y']))
    dz = abs(int(size['z']))
    vol = dx * dy * dz
    if vol == 0:
        return Counter()

    raw_pal = r_data.get('BlockStatePalette', [])
    palette = [str(entry.get('Name')) for entry in raw_pal]
    if not palette:
        return Counter()

    if len(palette) == 1:
        name = palette[0]
        return Counter({name: vol}) if name not in AIR_BLOCKS else Counter()

    bits_per_block = max(2, math.ceil(math.log2(len(palette))))
    mask = (1 << bits_per_block) - 1
    raw_longs = [int(x) & 0xFFFFFFFFFFFFFFFF for x in r_data.get('BlockStates', [])]

    counts: Counter[str] = Counter()
    for i in range(vol):
        start_bit = i * bits_per_block
        start_index = start_bit >> 6
        start_offset = start_bit & 0x3F
        end_bit = start_bit + bits_per_block - 1
        end_index = end_bit >> 6

        if start_index >= len(raw_longs):
            val = 0
        elif start_index == end_index:
            val = (raw_longs[start_index] >> start_offset) & mask
        else:
            part1 = raw_longs[start_index] >> start_offset
            part2 = raw_longs[end_index] << (64 - start_offset)
            val = (part1 | part2) & mask

        if val < len(palette):
            name = palette[val]
            if name not in AIR_BLOCKS:
                counts[name] += 1

    return counts


def parse_litematic(file_source: str | Path | io.BytesIO) -> dict[str, Any]:
    """Parse a ``.litematic`` file and return metadata, sections, and aggregated materials."""
    if isinstance(file_source, (str, Path)):
        nbt_data = nbtlib.load(str(file_source))
    else:
        file_source.seek(0)
        magic_number = file_source.read(2)
        file_source.seek(0)
        if magic_number == b'\x1f\x8b':
            with gzip.GzipFile(fileobj=file_source) as uncompressed:
                nbt_data = nbtlib.File.from_fileobj(uncompressed)
        else:
            nbt_data = nbtlib.File.from_fileobj(file_source)

    meta = nbt_data.get('Metadata', {})
    name = str(meta.get('Name') or 'Litematic Project')
    author = str(meta.get('Author') or 'Desconocido')
    total_blocks_meta = int(meta.get('TotalBlocks') or 0)
    total_volume_meta = int(meta.get('TotalVolume') or 0)

    regions_data = nbt_data.get('Regions', {})
    sorted_region_names = sorted(regions_data.keys(), key=natural_sort_key)

    global_materials: Counter[str] = Counter()
    sections: list[dict[str, Any]] = []

    for r_name in sorted_region_names:
        r_val = regions_data[r_name]
        pos = r_val.get('Position', {})
        size = r_val.get('Size', {})

        dx = abs(int(size.get('x', 0)))
        dy = abs(int(size.get('y', 0)))
        dz = abs(int(size.get('z', 0)))
        vol = dx * dy * dz

        counts = unpack_region_blocks(r_val)
        block_count = sum(counts.values())
        global_materials.update(counts)

        sections.append({
            'section': r_name,
            'blocks': block_count,
            'volume': vol,
            'position': (int(pos.get('x', 0)), int(pos.get('y', 0)), int(pos.get('z', 0))),
            'size': (int(size.get('x', 0)), int(size.get('y', 0)), int(size.get('z', 0))),
            'dimensions': f'{dx}x{dy}x{dz}',
            'status': '❌',
            'edited_by': None,
        })

    return {
        'title': name,
        'author': author,
        'total_blocks_meta': total_blocks_meta,
        'total_volume_meta': total_volume_meta,
        'total_blocks': sum(global_materials.values()),
        'sections': sections,
        'materials': global_materials.most_common(),
    }


def generate_carpet_csv(materials: list[tuple[str, int]]) -> str:
    """Generate CSV string compliant with Litematica / AeternumCarpet MaterialsStore."""
    output = io.StringIO()
    writer = csv.writer(output, lineterminator='\n')
    writer.writerow(['Item', 'Total', 'Missing', 'Available'])

    for raw_id, count in materials:
        writer.writerow([format_item_name(raw_id), count, 0, 0])

    return output.getvalue()


def export_to_carpet_csv(materials: list[tuple[str, int]], file_path: str | Path) -> None:
    """Write generated CSV directly to ``file_path``."""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(generate_carpet_csv(materials), encoding='utf-8')
