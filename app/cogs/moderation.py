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

    # --- Sistema de Sugerencias y Reclamos---
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        # Verifica si el canal de sugerencias/reclamos está configurado
        config = await self.bot.db_manager.get_guild_config(message.guild.id)
        if not config or not config.get("suggestion_channel_id"):
            return

        # Verifica si el mensaje se envia en el canal de sugerencias
        suggestion_channel_id = config["suggestion_channel_id"]
        if message.channel.id != suggestion_channel_id:
            return

        # Verifica si el mensaje es una sugerencia o un reclamo de lo contrario lo borramos
        if not message.content.startswith("Sugerencia:") or message.content.startswith(
            "Reclamo:"
        ):
            try:
                await message.delete()
            except discord.Forbidden:
                logger.warning(
                    f"No tengo permisos para eliminar mensajes en el canal {message.channel.id} del servidor {message.guild.id}."
                )
            except Exception as e:
                logger.error(f"Error al eliminar mensaje: {e}", exc_info=True)
            return

        # Agregar al mensaje una reaccion de "👍" y de "👎" si es una sugerencia
        if message.content.startswith("Sugerencia:"):
            await message.add_reaction("👍")
            await message.add_reaction("👎")

        # Agrega un hilo para que los usuarios puedan comentar sobre la sugerencia o reclamo
        try:
            thread = await message.create_thread(
                name=f"Sugerencia/Reclamo: {message.content[:50]}...",
                auto_archive_duration=60,  # Archivar automáticamente después de 60 minutos de inactividad
                reason="Creación automática de hilo para sugerencias/reclamos",
            )
            # Menciona al rol Staff en el hilo, si existe
            staff_role = discord.utils.get(message.guild.roles, name="Staff")
            staff_mention = staff_role.mention if staff_role else "@Staff"
            await thread.send(
                f"Gracias por tu sugerencia/reclamo, {message.author.mention}!\n "
                f"Por favor, usar este hilo para discutirlo.\n"
                f"Alguien del equipo del {staff_mention} se pondrá en contacto pronto. "
            )
        except discord.Forbidden:
            logger.warning(
                f"No tengo permisos para crear hilos en el canal {message.channel.id} del servidor {message.guild.id}."
            )
        except Exception as e:
            logger.error(
                f"Error al crear hilo para sugerencia/reclamo: {e}", exc_info=True
            )
            await message.channel.send(
                "Ocurrió un error al crear un hilo para tu sugerencia/reclamo. Por favor, intenta de nuevo más tarde."
            )

        return


# ==============================================================================
# Función de Carga del Cog
# ==============================================================================
async def setup(bot: commands.Bot):
    """Función para cargar el cog en el bot."""
    await bot.add_cog(Moderation(bot))
