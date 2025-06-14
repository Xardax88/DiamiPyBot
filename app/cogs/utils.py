import discord
from discord import app_commands 
from discord.ext import commands

class SlashUtils(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Muestra la latencia del bot.")
    async def ping(self, interaction: discord.Interaction):

        
        latencia = round(self.bot.latency * 1000)
        
        embed = discord.Embed(
            title="🏓 ¡Pong!",
            description=f"La latencia con la API de Discord es de **{latencia}ms**.",
            color=discord.Color.blue()
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(SlashUtils(bot))