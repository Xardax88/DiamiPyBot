# app/cogs/logging_events.py
import logging
import discord
from discord.ext import commands

logger = logging.getLogger("discord")

# ==============================================================================
# Cog para registrar eventos importantes del servidor
# ==============================================================================
class LoggingEvents(commands.Cog, name="logging"):
    """
    Cog encargado de registrar eventos importantes del servidor
    en un canal de historia designado.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _send_log_embed(self, guild_id: int, embed: discord.Embed):
        """Función auxiliar para enviar un embed al canal de historia."""
        config = await self.bot.db_manager.get_guild_config(guild_id)

        if not config or not config.get("features", {}).get(
            "history_channel_enabled", False
        ):
            return

        if not config or not config.get("history_channel_id"):
            return  # Si no hay canal configurado, no hacemos nada

        try:
            log_channel = self.bot.get_channel(config["history_channel_id"])
            if log_channel:
                await log_channel.send(embed=embed)
        except discord.Forbidden:
            logger.warning(
                f"No tengo permisos para enviar mensajes en el canal de historia del servidor {guild_id}."
            )
        except Exception as e:
            logger.error(f"Error al enviar log al servidor {guild_id}: {e}")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Se activa cuando un usuario se une al servidor."""
        embed = discord.Embed(
            title="✅ Usuario se ha unido",
            description=f"{member.mention} {member.name}",
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow(),
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="ID de Usuario", value=member.id, inline=False)
        embed.add_field(
            name="Cuenta Creada",
            value=discord.utils.format_dt(member.created_at, style="R"),
            inline=False,
        )
        embed.set_footer(text=f"Servidor: {member.guild.name}")

        await self._send_log_embed(member.guild.id, embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        """Se activa cuando un usuario abandona (o es expulsado/baneado) del servidor."""
        embed = discord.Embed(
            title="❌ Usuario ha salido",
            description=f"{member.mention} {member.name}",
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow(),
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="ID de Usuario", value=member.id, inline=False)
        embed.set_footer(text=f"Servidor: {member.guild.name}")

        await self._send_log_embed(member.guild.id, embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        """Se activa cuando un mensaje es eliminado."""
        if not message.guild or message.author.bot:
            return  # Ignorar mensajes de DMs o de otros bots

        content = (
            message.content
            or "El mensaje no tenía contenido de texto (posiblemente un embed o una imagen)."
        )

        embed = discord.Embed(
            title="🗑️ Mensaje Eliminado",
            description=f"**Autor:** {message.author.mention}\n**Canal:** {message.channel.mention}",
            color=discord.Color.orange(),
            timestamp=message.created_at,  # Muestra cuándo se creó el mensaje original
        )
        embed.add_field(
            name="Contenido", value=f"```{content[:1000]}```", inline=False
        )  # Truncamos a 1000 caracteres
        embed.set_footer(text=f"ID del Autor: {message.author.id}")

        await self._send_log_embed(message.guild.id, embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        """Se activa cuando un mensaje es editado."""
        if not after.guild or after.author.bot or before.content == after.content:
            return  # Ignorar DMs, bots, o ediciones que no cambian el texto (ej. carga de embeds)

        before_content = before.content or "N/A"
        after_content = after.content or "N/A"

        embed = discord.Embed(
            title="✏️ Mensaje Editado",
            description=f"**Autor:** {after.author.mention}\n**Canal:** {after.channel.mention}\n[Ir al mensaje]({after.jump_url})",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow(),
        )
        embed.add_field(
            name="Contenido Anterior",
            value=f"```{before_content[:1000]}```",
            inline=False,
        )
        embed.add_field(
            name="Contenido Nuevo", value=f"```{after_content[:1000]}```", inline=False
        )
        embed.set_footer(text=f"ID del Autor: {after.author.id}")

        await self._send_log_embed(after.guild.id, embed)

# ==============================================================================
# FUNCIÓN DE CARGA DEL COG
# ==============================================================================
async def setup(bot: commands.Bot):
    """Función para cargar el cog en el bot."""
    await bot.add_cog(LoggingEvents(bot))
