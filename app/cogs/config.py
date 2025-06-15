# cogs/config.py
import discord
from discord import app_commands
from discord.ext import commands

# Creamos un Command Group para anidar los subcomandos bajo /configurar
# Solo los administradores podrán ver y usar estos comandos.
@app_commands.default_permissions(administrator=True)
class Config(commands.GroupCog, name="configurar"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        super().__init__()

    @app_commands.command(name="canal_principal", description="Establece el canal principal para anuncios.")
    @app_commands.describe(canal="El canal que quieres designar como principal.")
    async def set_main_channel(self, interaction: discord.Interaction, canal: discord.TextChannel):
        """Establece el canal principal."""
        if not interaction.guild:
            return # Este comando no puede usarse en DMs

        await self.bot.db_manager.update_channel(
            interaction.guild.id,
            "main_channel_id",
            canal.id
        )

        embed = discord.Embed(
            title="✅ Configuración Actualizada",
            description=f"El canal principal ha sido establecido en {canal.mention}.",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="canal_logs", description="Establece el canal para recibir logs del bot.")
    @app_commands.describe(canal="El canal donde se enviarán los logs.")
    async def set_log_channel(self, interaction: discord.Interaction, canal: discord.TextChannel):
        """Establece el canal de logs."""
        if not interaction.guild:
            return

        await self.bot.db_manager.update_channel(
            interaction.guild.id,
            "log_channel_id",
            canal.id
        )
        embed = discord.Embed(
            title="✅ Configuración Actualizada",
            description=f"El canal de logs ha sido establecido en {canal.mention}.",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="canal_reglas", description="Establece el canal de reglas del servidor.")
    @app_commands.describe(canal="El canal donde están publicadas las reglas.")
    async def set_rules_channel(self, interaction: discord.Interaction, canal: discord.TextChannel):
        """Establece el canal de reglas."""
        if not interaction.guild:
            return

        await self.bot.db_manager.update_channel(
            interaction.guild.id,
            "rules_channel_id",
            canal.id
        )
        embed = discord.Embed(
            title="✅ Configuración Actualizada",
            description=f"El canal de reglas ha sido establecido en {canal.mention}.",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="canal_confesiones", description="Establece el canal de confesiones.")
    @app_commands.describe(canal="El canal donde se publican la confesiones anonimas.")
    async def set_confession_channel(self, interaction: discord.Interaction, canal: discord.TextChannel):
        """Establece el canal de reglas."""
        if not interaction.guild:
            return

        await self.bot.db_manager.update_channel(
            interaction.guild.id,
            "confession_channel_id",
            canal.id
        )

        embed = discord.Embed(
            title="✅ Configuración Actualizada",
            description=f"El canal de confesiones ha sido establecido en {canal.mention}.",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="canal_historia",
                          description="Establece el canal para el historial de eventos (joins, edits, deletes).")
    @app_commands.describe(canal="El canal donde se enviará el historial de moderación.")
    async def set_history_channel(self, interaction: discord.Interaction, canal: discord.TextChannel):
        """Establece el canal del historial de eventos."""
        if not interaction.guild:
            return

        await self.bot.db_manager.update_channel(
            interaction.guild.id,
            "history_channel_id",  # La clave que coincide con la DB
            canal.id
        )

        embed = discord.Embed(
            title="✅ Configuración Actualizada",
            description=f"El canal de historia ha sido establecido en {canal.mention}.",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    """Función para cargar el cog en el bot."""
    await bot.add_cog(Config(bot))