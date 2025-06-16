# app/cogs/moderation.py
import logging
import discord
from discord import app_commands
from discord.ext import commands

logger = logging.getLogger(__name__)


# ==============================================================================
# Cog para comandos de moderación
# ==============================================================================
class Moderation(commands.Cog, name="Moderation"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # --- Comando Slash para reportar usuarios ---
    @app_commands.command(
        name="report",
        description="📣 Reporta a un usuario a la moderación del servidor.",
    )
    @app_commands.describe(
        usuario="El miembro del servidor que quieres reportar.",
        razon="El motivo del reporte. Por favor, sé lo más específico posible.",
    )
    async def report_user(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member,
        razon: str,
    ):
        """Envía un reporte detallado a un canal de moderación privado."""
        if not interaction.guild:
            # Este comando no tiene sentido fuera de un servidor.
            return

        # 1. Verificar si el usuario se está reportando a sí mismo.
        if usuario.id == interaction.user.id:
            await interaction.response.send_message(
                "No puedes reportarte a ti mismo.", ephemeral=True
            )
            return

        # 2. Obtener la configuración del servidor.
        config = await self.bot.db_manager.get_guild_config(interaction.guild.id)
        if not (config and (channel_id := config.get("report_channel_id"))):
            await interaction.response.send_message(
                "El sistema de reportes no está configurado en este servidor. Por favor, contacta a un administrador.",
                ephemeral=True,
            )
            return

        report_channel = self.bot.get_channel(channel_id)
        if not report_channel:
            await interaction.response.send_message(
                "No puedo encontrar el canal de reportes. Puede que haya sido eliminado o necesite permisos.",
                ephemeral=True,
            )
            return

        # 3. Crear el embed informativo para los moderadores.
        embed = discord.Embed(
            title="🚨 Nuevo Reporte de Usuario",
            color=discord.Color.orange(),
            timestamp=discord.utils.utcnow(),
        )

        embed.set_author(
            name=f"Reporte iniciado por {interaction.user.name}",
            icon_url=interaction.user.display_avatar.url,
        )

        embed.add_field(
            name="👤 Usuario Reportado",
            value=f"{usuario.mention} (`{usuario.id}`)",
            inline=False,
        )
        embed.add_field(
            name="억 Reportado Por",
            value=f"{interaction.user.mention} (`{interaction.user.id}`)",
            inline=False,
        )
        embed.add_field(
            name="📜 Razón del Reporte", value=f"```{razon}```", inline=False
        )
        embed.add_field(
            name="📍 Canal del Reporte",
            value=(
                f"{interaction.channel.mention}"
                if interaction.channel
                else "No disponible"
            ),
            inline=False,
        )

        embed.set_footer(text=f"Servidor: {interaction.guild.name}")

        # 4. Enviar el reporte y confirmar al usuario.
        try:
            await report_channel.send(embed=embed)
            await interaction.response.send_message(
                "✅ Tu reporte ha sido enviado confidencialmente a la moderación. ¡Gracias por ayudar a mantener la comunidad segura!",
                ephemeral=True,
                delete_after=15,
            )
        except discord.Forbidden:
            logger.warning(
                f"No se pudo enviar reporte en '{interaction.guild.name}' por falta de permisos en el canal de reportes."
            )
            await interaction.response.send_message(
                "Ocurrió un error al enviar tu reporte (posiblemente un problema de permisos). Por favor, avisa a un administrador.",
                ephemeral=True,
            )
        except Exception as e:
            logger.error(f"Error inesperado al enviar reporte: {e}", exc_info=True)
            await interaction.response.send_message(
                "Ocurrió un error inesperado al enviar tu reporte. Inténtalo de nuevo más tarde.",
                ephemeral=True,
            )


# ==============================================================================
# Función de Carga del Cog
# ==============================================================================
async def setup(bot: commands.Bot):
    """Función para cargar el cog en el bot."""
    await bot.add_cog(Moderation(bot))
