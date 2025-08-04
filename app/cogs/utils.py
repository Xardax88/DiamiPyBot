# cogs/general.py
import os
import logging
import discord
from discord.ext import commands
from discord import app_commands, ui, TextStyle
import random

logger = logging.getLogger(__name__)


# ==============================================================================
# Cog para comandos generales del bot
# ==============================================================================
class Utils(commands.Cog, name="Utils"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # --- Comando Slash para mostrar la latencia del bot ---
    @app_commands.command(
        name="ping",
        description="📈 Muestra la latencia del bot con el servidor de Discord.",
    )
    async def ping(self, interaction: discord.Interaction):
        """Muestra la latencia actual del bot."""
        latency = round(self.bot.latency * 1000)
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"La latencia actual es de **{latency}ms**.",
            color=discord.Color.green() if latency < 150 else discord.Color.orange(),
        )
        logger.info(
            f"{interaction.guild.name}: {latency}ms",
            extra={"guild_id": interaction.guild.id},
        )
        await interaction.response.send_message(embed=embed)

    # --- Comando Slash para mostrar el avatar de un usuario ---
    @app_commands.command(
        name="avatar",
        description="🖼️ Muestra el avatar de un usuario o el tuyo si no se especifica.",
    )
    @app_commands.describe(
        usuario="El usuario del que quieres ver el avatar (opcional)"
    )
    async def avatar(
        self, interaction: discord.Interaction, usuario: discord.User = None
    ):
        """
        Muestra el avatar de un usuario especificado o el propio si no se indica ninguno.
        """
        # Si no se especifica usuario, usar el autor de la interacción
        objetivo = usuario or interaction.user
        avatar_url = objetivo.display_avatar.url
        embed = discord.Embed(
            title=f"Avatar de {objetivo.display_name}",
            color=discord.Color.blue(),
        )
        embed.set_image(url=avatar_url)
        await interaction.response.send_message(embed=embed)

    # --- Comando Slash para mostrar información de un usuario ---
    @app_commands.command(
        name="userinfo",
        description="ℹ️ Muestra información de un usuario o la tuya si no se especifica.",
    )
    @app_commands.describe(
        usuario="El usuario del que quieres ver la información (opcional)"
    )
    async def userinfo(
        self, interaction: discord.Interaction, usuario: discord.User = None
    ):
        """
        Muestra información detallada de un usuario especificado o del propio usuario si no se indica ninguno.
        """
        objetivo = usuario or interaction.user
        # Construir el embed con información relevante
        embed = discord.Embed(
            title=f"Información de {objetivo.display_name}",
            color=discord.Color.purple(),
            timestamp=objetivo.created_at,
        )
        embed.set_thumbnail(url=objetivo.display_avatar.url)
        embed.add_field(name="ID", value=objetivo.id, inline=True)
        embed.add_field(name="Nombre de usuario", value=f"{objetivo}", inline=True)
        embed.add_field(
            name="Cuenta creada",
            value=objetivo.created_at.strftime("%d/%m/%Y %H:%M"),
            inline=False,
        )
        # Si el usuario es miembro del servidor, mostrar información adicional
        if isinstance(objetivo, discord.Member):
            embed.add_field(
                name="Entró al servidor",
                value=objetivo.joined_at.strftime("%d/%m/%Y %H:%M"),
                inline=False,
            )
            roles = [
                role.mention for role in objetivo.roles if role.name != "@everyone"
            ]
            embed.add_field(
                name="Roles",
                value=", ".join(roles) if roles else "Sin roles",
                inline=False,
            )
            embed.add_field(
                name="Bot", value="Sí" if objetivo.bot else "No", inline=True
            )
        else:
            embed.add_field(
                name="Bot", value="Sí" if objetivo.bot else "No", inline=True
            )
        await interaction.response.send_message(embed=embed)


# ==============================================================================
# FUNCIÓN DE CARGA DEL COG
# ==============================================================================
async def setup(bot: commands.Bot):
    await bot.add_cog(Utils(bot))
