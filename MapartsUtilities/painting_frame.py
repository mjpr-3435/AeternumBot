from __future__ import annotations

import importlib.util
import io
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PIL import Image

_ASSETS_DIR = Path(__file__).resolve().parent / 'assets'
_BORDER_TEXTURE_PATH = _ASSETS_DIR / 'kebab.png'
_MAX_DIMENSION = 8192
_PIXEL_GRID_TARGET = 48
_PIXEL_UPSCALE_MIN = 720
_DEFAULT_BORDER_RATIO = 0.016


class PaintingFrameError(Exception):
    """Error controlado al validar o enmarcar una imagen."""


@dataclass(frozen=True, slots=True)
class FrameResult:
    data: bytes
    filename: str
    width: int
    height: int
    pixelated: bool


def ensure_pillow() -> bool:
    """Verifica si ``Pillow`` está instalado y lo instala automáticamente si falta.

    Retorna ``True`` si tuvo que instalarlo en esta ejecución, ``False`` si ya estaba disponible.
    """
    if importlib.util.find_spec('PIL') is not None:
        return False

    proc = subprocess.run(
        [sys.executable, '-m', 'pip', 'install', 'Pillow>=10.0.0'],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or 'Error desconocido').strip()
        raise PaintingFrameError(f'No se pudo instalar `Pillow` automáticamente:\n```\n{detail[-600:]}\n```')
    return True


def _build_framed_image(inner: Image.Image, border_tex: Image.Image, border_px: int) -> Image.Image:
    """Aplica el borde de 1 px de ``border_tex`` escalado a ``border_px`` alrededor de ``inner``."""
    from PIL import Image

    w, h = inner.size
    out_w = w + 2 * border_px
    out_h = h + 2 * border_px
    canvas = Image.new('RGBA', (out_w, out_h))

    # Esquinas (1x1 -> border_px x border_px)
    corners = (
        ((0, 0, 1, 1), (0, 0)),
        ((15, 0, 16, 1), (out_w - border_px, 0)),
        ((0, 15, 1, 16), (0, out_h - border_px)),
        ((15, 15, 16, 16), (out_w - border_px, out_h - border_px)),
    )
    for crop_box, dest in corners:
        corner = border_tex.crop(crop_box).resize((border_px, border_px), Image.Resampling.NEAREST)
        canvas.paste(corner, dest)

    # Bordes superior e inferior (tira de 14x1 repetida)
    top_tile = border_tex.crop((1, 0, 15, 1)).resize((14 * border_px, border_px), Image.Resampling.NEAREST)
    bot_tile = border_tex.crop((1, 15, 15, 16)).resize((14 * border_px, border_px), Image.Resampling.NEAREST)
    for x in range(border_px, out_w - border_px, top_tile.width):
        chunk_w = min(top_tile.width, out_w - border_px - x)
        canvas.paste(top_tile.crop((0, 0, chunk_w, border_px)), (x, 0))
        canvas.paste(bot_tile.crop((0, 0, chunk_w, border_px)), (x, out_h - border_px))

    # Bordes izquierdo y derecho (tira de 1x14 repetida)
    left_tile = border_tex.crop((0, 1, 1, 15)).resize((border_px, 14 * border_px), Image.Resampling.NEAREST)
    right_tile = border_tex.crop((15, 1, 16, 15)).resize((border_px, 14 * border_px), Image.Resampling.NEAREST)
    for y in range(border_px, out_h - border_px, left_tile.height):
        chunk_h = min(left_tile.height, out_h - border_px - y)
        canvas.paste(left_tile.crop((0, 0, border_px, chunk_h)), (0, y))
        canvas.paste(right_tile.crop((0, 0, border_px, chunk_h)), (out_w - border_px, y))

    canvas.paste(inner, (border_px, border_px))
    return canvas


def apply_minecraft_frame(
    raw_data: bytes,
    *,
    source_name: str = 'imagen.png',
    pixelar: bool = False,
    border_ratio: float = _DEFAULT_BORDER_RATIO,
) -> FrameResult:
    """Aplica un marco real de cuadro de Minecraft alrededor de una imagen.

    Si ``pixelar`` es ``True``, reduce primero la imagen a estilo pixel-art de Minecraft
    antes de aplicar el borde de 1 px y reescalar con ``NEAREST``.
    """
    ensure_pillow()
    from PIL import Image, ImageOps, UnidentifiedImageError

    if not _BORDER_TEXTURE_PATH.is_file():
        raise PaintingFrameError(f'No se encontró la textura del marco en `{_BORDER_TEXTURE_PATH.name}`.')

    try:
        with Image.open(io.BytesIO(raw_data)) as opened:
            src = ImageOps.exif_transpose(opened).convert('RGBA')
    except UnidentifiedImageError as exc:
        raise PaintingFrameError('El archivo no es una imagen válida o el formato no está soportado.') from exc

    w, h = src.size
    if w < 2 or h < 2:
        raise PaintingFrameError('La imagen es demasiado pequeña (mínimo 2×2 píxeles).')
    if w > _MAX_DIMENSION or h > _MAX_DIMENSION:
        raise PaintingFrameError(f'La imagen supera el máximo permitido de {_MAX_DIMENSION}×{_MAX_DIMENSION} píxeles.')

    border_tex = Image.open(_BORDER_TEXTURE_PATH).convert('RGBA')

    if pixelar:
        scale_down = _PIXEL_GRID_TARGET / max(w, h)
        grid_w = max(8, round(w * scale_down))
        grid_h = max(8, round(h * scale_down))
        pixel_art = src.resize((grid_w, grid_h), Image.Resampling.LANCZOS)
        framed_grid = _build_framed_image(pixel_art, border_tex, border_px=1)
        upscale = max(1, round(_PIXEL_UPSCALE_MIN / max(framed_grid.size)))
        result_img = framed_grid.resize(
            (framed_grid.width * upscale, framed_grid.height * upscale),
            Image.Resampling.NEAREST,
        )
    else:
        border_px = max(6, round(min(w, h) * border_ratio))
        result_img = _build_framed_image(src, border_tex, border_px=border_px)

    out_buf = io.BytesIO()
    result_img.save(out_buf, format='PNG')
    stem = Path(source_name).stem or 'imagen'
    return FrameResult(
        data=out_buf.getvalue(),
        filename=f'{stem}_mc_frame.png',
        width=result_img.width,
        height=result_img.height,
        pixelated=pixelar,
    )
