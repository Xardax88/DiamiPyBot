# cogs/general.py
import discord
from discord.ext import commands
from discord import app_commands


class General(commands.Cog):
    """
    Un cog para comandos generales y de utilidad.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # --- Comando Slash: /ping ---
    @app_commands.command(name="ping", description="Muestra la latencia del bot con el servidor de Discord.")
    async def ping(self, interaction: discord.Interaction):
        """Responde con la latencia del bot en milisegundos."""
        # La latencia del bot está en segundos, la multiplicamos por 1000 para obtener ms.
        latency = round(self.bot.latency * 1000)

        # Creamos un embed para una respuesta más bonita
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"La latencia actual es de **{latency}ms**.",
            color=discord.Color.green() if latency < 150 else discord.Color.orange()
        )

        # 'interaction.response.send_message' es la forma de responder a un comando slash.
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    """
    Función especial que discord.py busca al cargar una extensión.
    """
    await bot.add_cog(General(bot))