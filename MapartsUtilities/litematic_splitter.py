from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from litemapy import BlockState, Region, Schematic

_AIR_IDS = frozenset({'minecraft:air', 'minecraft:cave_air', 'minecraft:void_air'})
_STACK_16_SUFFIXES = ('_banner', '_sign', '_hanging_sign')
_STACK_1_KEYWORDS = ('_bed', 'shulker_box', 'decorated_pot', 'chest', 'skull', 'head')


class MapartSplitError(Exception):
    """Error controlado al validar o dividir un archivo .litematic."""


@dataclass(frozen=True, slots=True)
class RegionSummary:
    name: str
    width: int
    length: int
    slots: int
    blocks: int


@dataclass(frozen=True, slots=True)
class SplitResult:
    data: bytes
    filename: str
    width: int
    length: int
    total_blocks: int
    regions: tuple[RegionSummary, ...]


def ensure_litemapy() -> bool:
    """Verifica si ``litemapy`` está instalado y lo instala automáticamente si falta.

    Retorna ``True`` si tuvo que instalarlo en esta ejecución, ``False`` si ya estaba disponible.
    """
    if importlib.util.find_spec('litemapy') is not None:
        return False

    proc = subprocess.run(
        [sys.executable, '-m', 'pip', 'install', 'litemapy>=0.11.0b0'],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or 'Error desconocido').strip()
        raise MapartSplitError(f'No se pudo instalar `litemapy` automáticamente:\n```\n{detail[-600:]}\n```')

    importlib.invalidate_caches()
    return True


def _stack_size_for_block(block_id: str) -> int:
    name = block_id.removeprefix('minecraft:')
    if name.endswith(_STACK_16_SUFFIXES):
        return 16
    if any(kw in name for kw in _STACK_1_KEYWORDS) and 'ender_chest' not in name and 'trapped_chest' not in name:
        if name.endswith('_bed') or 'shulker_box' in name:
            return 1
    return 64


def _load_schematic_from_bytes(data: bytes) -> Schematic:
    from litemapy import Schematic

    with tempfile.NamedTemporaryFile(suffix='.litematic', delete=False) as tmp:
        tmp.write(data)
        tmp_path = Path(tmp.name)

    try:
        return Schematic.load(str(tmp_path))
    except Exception as exc:
        raise MapartSplitError(f'No se pudo leer el archivo `.litematic`: {exc}') from exc
    finally:
        tmp_path.unlink(missing_ok=True)


def _save_schematic_to_bytes(schem: Schematic) -> bytes:
    with tempfile.NamedTemporaryFile(suffix='.litematic', delete=False) as tmp:
        tmp_path = Path(tmp.name)

    try:
        schem.save(str(tmp_path))
        return tmp_path.read_bytes()
    finally:
        tmp_path.unlink(missing_ok=True)


def _extract_2d_grid(region: Region) -> tuple[np.ndarray, list[BlockState], np.ndarray]:
    """Convierte una región 2D (altura Y=1) en una matriz (width, length) de índices de paleta."""
    min_x, max_x = region.min_x(), region.max_x()
    min_y = region.min_y()
    min_z, max_z = region.min_z(), region.max_z()

    width = max_x - min_x + 1
    length = max_z - min_z + 1

    grid = np.zeros((width, length), dtype=np.int32)
    state_to_idx: dict[BlockState, int] = {}
    states: list[BlockState] = []
    stacks: list[int] = [64]  # índice 0 reservado para aire

    for lx in range(width):
        rx = min_x + lx
        for lz in range(length):
            rz = min_z + lz
            block = region[rx, min_y, rz]
            if block.id in _AIR_IDS:
                continue
            idx = state_to_idx.get(block)
            if idx is None:
                idx = len(states) + 1
                state_to_idx[block] = idx
                states.append(block)
                stacks.append(_stack_size_for_block(block.id))
            grid[lx, lz] = idx

    return grid, states, np.array(stacks, dtype=np.int32)


def _count_slots(subgrid: np.ndarray, stack_sizes: np.ndarray) -> tuple[int, int]:
    """Devuelve ``(slots_ocupados, total_bloques)`` para un rectángulo de la matriz."""
    flat = subgrid.ravel()
    counts = np.bincount(flat, minlength=len(stack_sizes))
    non_air_counts = counts[1:]
    mask = non_air_counts > 0
    if not np.any(mask):
        return 0, 0

    active_counts = non_air_counts[mask]
    active_stacks = stack_sizes[1:][mask]
    slots = int(np.sum((active_counts + active_stacks - 1) // active_stacks))
    blocks = int(np.sum(active_counts))
    return slots, blocks


def _split_rectangles(
    grid: np.ndarray,
    stack_sizes: np.ndarray,
    max_slots: int,
) -> list[tuple[int, int, int, int, int, int]]:
    """Divide recursivamente en rectángulos hasta que cada uno ocupe ``<= max_slots``."""
    width, length = grid.shape
    results: list[tuple[int, int, int, int, int, int]] = []
    stack: list[tuple[int, int, int, int]] = [(0, width, 0, length)]

    while stack:
        x0, x1, z0, z1 = stack.pop()
        slots, blocks = _count_slots(grid[x0:x1, z0:z1], stack_sizes)
        if blocks == 0:
            continue

        w = x1 - x0
        l = z1 - z0
        if slots <= max_slots or (w <= 1 and l <= 1):
            results.append((x0, x1, z0, z1, slots, blocks))
            continue

        if w >= l:
            mid = (x0 + x1) // 2
            stack.append((mid, x1, z0, z1))
            stack.append((x0, mid, z0, z1))
        else:
            mid = (z0 + z1) // 2
            stack.append((x0, x1, mid, z1))
            stack.append((x0, x1, z0, mid))

    results.sort(key=lambda r: (r[2], r[0]))
    return results


def split_mapart_litematic(
    data: bytes,
    *,
    max_slots: int = 27,
    source_name: str = 'mapart',
) -> SplitResult:
    """Valida que el `.litematic` sea 2D y lo divide en sub-regiones rectangulares de hasta ``max_slots``."""
    if max_slots < 1:
        raise MapartSplitError('`max_slots` debe ser mayor o igual a 1.')

    ensure_litemapy()
    from litemapy import Region, Schematic

    schem = _load_schematic_from_bytes(data)

    if len(schem.regions) == 0:
        raise MapartSplitError('El archivo `.litematic` no contiene ninguna región.')
    if len(schem.regions) > 1:
        raise MapartSplitError(
            f'El archivo tiene {len(schem.regions)} regiones. Sube un mapart de 1 sola región sin dividir.'
        )

    orig_region = next(iter(schem.regions.values()))
    if abs(orig_region.height) != 1:
        raise MapartSplitError(
            f'Este archivo no es un mapart 2D (altura Y = {abs(orig_region.height)}, debe ser 1).'
        )

    grid, states, stack_sizes = _extract_2d_grid(orig_region)
    rects = _split_rectangles(grid, stack_sizes, max_slots)
    if not rects:
        raise MapartSplitError('El mapart está vacío (solo contiene aire).')

    base_x = orig_region.min_schem_x()
    base_y = orig_region.min_schem_y()
    base_z = orig_region.min_schem_z()

    stem = Path(source_name).stem or 'mapart'
    out_schem = Schematic(
        name=f'{schem.name or stem} (Split {max_slots}s)',
        author=schem.author or 'AeternumBot',
        description=f'Dividido en {len(rects)} regiones de máximo {max_slots} slots.',
        lm_version=schem.lm_version,
        mc_version=schem.mc_version,
    )

    summaries: list[RegionSummary] = []
    total_blocks = 0

    for idx, (x0, x1, z0, z1, slots, blocks) in enumerate(rects, start=1):
        w = x1 - x0
        l = z1 - z0
        reg_name = f'R{idx:03d}_{slots}s'
        sub_region = Region(base_x + x0, base_y, base_z + z0, w, 1, l)

        subgrid = grid[x0:x1, z0:z1]
        for lx in range(w):
            for lz in range(l):
                state_idx = int(subgrid[lx, lz])
                if state_idx != 0:
                    sub_region[lx, 0, lz] = states[state_idx - 1]

        out_schem.regions[reg_name] = sub_region
        summaries.append(RegionSummary(name=reg_name, width=w, length=l, slots=slots, blocks=blocks))
        total_blocks += blocks

    out_bytes = _save_schematic_to_bytes(out_schem)
    out_filename = f'{stem}_split.litematic'

    return SplitResult(
        data=out_bytes,
        filename=out_filename,
        width=grid.shape[0],
        length=grid.shape[1],
        total_blocks=total_blocks,
        regions=tuple(summaries),
    )
