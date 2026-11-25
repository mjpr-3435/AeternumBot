from __future__ import annotations

import discord

_EMBED_COLOUR = 0x2F3136


def interviewer_rules_embed(thumbnail: str) -> discord.Embed:
    """Build the ephemeral rules embed for interviewers."""
    return discord.Embed(
        title='> Reglas para entrevistadores',
        colour=_EMBED_COLOUR,
        description=(
            '- Los entrevistadores tienen permisos para agregar o remover personas de la whitelist. '
            'Esta función debe utilizarse únicamente al otorgar o revocar la membresía de un usuario, '
            'y solo respecto a esa persona.\n'
            '- Toda persona que desee ingresar al servidor como miembro debe enviar su formulario, '
            'con el fin de que todos los entrevistadores la conozcan. '
            'Si es conocida por todos y no existe oposición de ninguno, el formulario puede omitirse, '
            'pero la entrevista siempre es obligatoria.\n'
            '- En caso de invitar a alguien al servidor de forma temporal '
            '(por ejemplo, para una visita breve o para usar los servidores de Aeternum bajo '
            'condiciones especiales), dicha invitación debe ser aprobada explícitamente por todos los '
            'entrevistadores.\n'
            '- Los formularios sin evidencias deben rechazarse; no obstante, existe cierto margen de '
            'criterio. Todos los postulantes deben contar con micrófono; de lo contrario, no pueden '
            'ser aceptados para evitar suplantaciones de identidad.'
        ),
    ).set_thumbnail(url=thumbnail)


def interviews_embed(thumbnail: str) -> discord.Embed:
    """Build the ephemeral interview guide embed."""
    return discord.Embed(
        title='> Entrevistas',
        colour=_EMBED_COLOUR,
        description=(
            'Las entrevistas se realizan para conocer al postulante y evaluar su encaje en el servidor. '
            'La entrevista es dirigida por un único entrevistador.\n'
            '- Se inicia con preguntas generales (vida personal y relación con el Minecraft técnico).\n'
            '- Luego se pasa a preguntas específicas sobre su experiencia en el rol.\n'
            '- Los entrevistadores presentes pueden intervenir antes de la deliberación.\n'
            '- Se silencia y ensordece al postulante para deliberar.\n'
            '- Se comunica la decisión y, en caso de aceptación, se asignan roles y whitelist.\n'
            '- Se explica el uso del Discord y se remite a la guía del servidor.'
        ),
    ).set_thumbnail(url=thumbnail)


def ticket_tools_embed(thumbnail: str) -> discord.Embed:
    """Build the ephemeral ``/ticket`` documentation embed."""
    return discord.Embed(
        title='Comando /ticket',
        colour=_EMBED_COLOUR,
        description=(
            'Sirve para actualizar el estado del ticket del postulante.\n'
            '> `/ticket <estado> <ping>`\n\n'
            '**Estados**\n'
            '- `Accept` : marca aceptado y envia el mensaje para coordinar entrevista.\n'
            '- `Reject` : marca rechazado y envia el rechazo.\n'
            '- `Voting` : deja el ticket en revision.\n'
            '- `Incomplete` : marca el ticket como incompleto.'
        ),
    ).set_thumbnail(url=thumbnail)


class InterviewersInfoView(discord.ui.View):
    """Persistent action buttons for the InterviewersInfo banner."""

    def __init__(self, thumbnail: str) -> None:
        super().__init__(timeout=None)
        self._thumbnail = thumbnail

    @discord.ui.button(
        label='Reglas',
        style=discord.ButtonStyle.gray,
        custom_id='interviewers:rules',
    )
    async def rules_button(
        self,
        interaction: discord.Interaction,
        _button: discord.ui.Button[InterviewersInfoView],
    ) -> None:
        await interaction.response.send_message(
            embed=interviewer_rules_embed(self._thumbnail),
            ephemeral=True,
        )

    @discord.ui.button(
        label='Entrevistas',
        style=discord.ButtonStyle.gray,
        custom_id='interviewers:interviews',
    )
    async def interviews_button(
        self,
        interaction: discord.Interaction,
        _button: discord.ui.Button[InterviewersInfoView],
    ) -> None:
        await interaction.response.send_message(
            embed=interviews_embed(self._thumbnail),
            ephemeral=True,
        )

    @discord.ui.button(
        label='/Ticket',
        style=discord.ButtonStyle.gray,
        custom_id='interviewers:ticket',
    )
    async def ticket_button(
        self,
        interaction: discord.Interaction,
        _button: discord.ui.Button[InterviewersInfoView],
    ) -> None:
        await interaction.response.send_message(
            embed=ticket_tools_embed(self._thumbnail),
            ephemeral=True,
        )
