from __future__ import annotations

import asyncio
import io

import discord
from discord import app_commands
from discord.ext import commands
from dismanager.classes import DisManagerClient
from MapartsUtilities.litematic_splitter import MapartSplitError, split_mapart_litematic

_MAX_FILE_BYTES = 10 * 1024 * 1024


class MapartCommandCog(commands.Cog):
    """Comandos de Discord para utilidades de maparts 2D (.litematic)."""

    def __init__(self, client: DisManagerClient) -> None:
        self.client = client

    @app_commands.command(
        name='splitmap',
        description='Divide un mapart 2D (.litematic) en regiones rectangulares de máximo 27 slots.',
    )
    @app_commands.describe(
        archivo='Archivo .litematic del mapart 2D',
    )
    async def splitmap(
        self,
        interaction: discord.Interaction,
        archivo: discord.Attachment,
    ) -> None:
        if not archivo.filename.lower().endswith('.litematic'):
            await interaction.response.send_message(
                '✖ El archivo debe tener extensión `.litematic`.',
                ephemeral=True,
            )
            return

        if archivo.size > _MAX_FILE_BYTES:
            await interaction.response.send_message(
                '✖ El archivo supera el límite de 10 MB.',
                ephemeral=True,
            )
            return

        await interaction.response.defer(thinking=True)

        try:
            raw_data = await archivo.read()
            result = await asyncio.to_thread(
                split_mapart_litematic,
                raw_data,
                source_name=archivo.filename,
            )
        except MapartSplitError as exc:
            await interaction.followup.send(f'✖ {exc}')
            return
        except Exception as exc:
            await interaction.followup.send(f'✖ Error inesperado procesando el `.litematic`: {exc}')
            return

        slots_list = [r.slots for r in result.regions]
        avg_slots = sum(slots_list) / len(slots_list)
        summary = (
            f'✔ **{result.filename}**\n'
            f'- **Dimensiones:** `{result.width} × {result.length}` (`{result.total_blocks:,}` bloques)\n'
            f'- **Regiones:** `{len(result.regions)}` (máx. `27` slots)\n'
            f'- **Slots/región:** mín `{min(slots_list)}` · prom `{avg_slots:.1f}` · máx `{max(slots_list)}`'
        )
        out_file = discord.File(io.BytesIO(result.data), filename=result.filename)
        await interaction.followup.send(content=summary, file=out_file)


async def setup(client: DisManagerClient) -> None:
    """Register the MapartCommandCog on ``client``."""
    await client.add_cog(MapartCommandCog(client))
