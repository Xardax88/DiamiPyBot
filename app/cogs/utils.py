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


# ==============================================================================
# FUNCIÓN DE CARGA DEL COG
# ==============================================================================
async def setup(bot: commands.Bot):
    await bot.add_cog(Utils(bot))
