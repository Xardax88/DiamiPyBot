# app/cogs/config.py
import discord
from discord import app_commands
from discord.ext import commands


@app_commands.default_permissions(administrator=True)
class Config(commands.GroupCog, name="config"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        super().__init__()

    # COMANDO PARA VER LA CONFIGURACIÓN
    @app_commands.command(name="ver", description="Muestra la configuración actual de los canales del servidor.")
    async def view_config(self, interaction: discord.Interaction):
        """Muestra todos los canales configurados en un embed."""
        if not interaction.guild:
            return

        await interaction.response.defer(ephemeral=True)

        config = await self.bot.db_manager.get_guild_config(interaction.guild.id)

        embed = discord.Embed(
            title="⚙️ Configuración de Canales",
            description=f"Estado actual de la configuración para **{interaction.guild.name}**.",
            color=discord.Color.blue()
        )

        if not config:
            embed.description = "No hay ninguna configuración guardada para este servidor todavía. Usa los subcomandos de `/config` para empezar."
            await interaction.followup.send(embed=embed)
            return

        # Mapeo de claves de la DB a nombres legibles
        channel_map = {
            "main_channel_id": "Canal Principal",
            "log_channel_id": "Canal de Logs",
            "rules_channel_id": "Canal de Reglas",
            "history_channel_id": "Canal de Historia",
            "confession_channel_id": "Canal de Confesiones",
        }

        for key, name in channel_map.items():
            channel_id = config.get(key)
            value = "Sin configurar"  # Valor por defecto

            if channel_id:
                channel = interaction.guild.get_channel(channel_id)
                if channel:
                    value = channel.mention
                else:
                    # El ID está en la DB, pero el canal ya no existe en el servidor.
                    value = f"⚠️ Canal no encontrado (ID: `{channel_id}`)"

            embed.add_field(name=f"▶️ {name}", value=value, inline=False)

        await interaction.followup.send(embed=embed)

    # COMANDOS PARA ESTABLECER CANALES
    @app_commands.command(name="canal_principal", description="Establece el canal principal.")
    @app_commands.describe(canal="El canal que quieres designar como principal.")
    async def set_main_channel(self, interaction: discord.Interaction, canal: discord.TextChannel):
        """Establece el canal principal del servidor."""
        if not interaction.guild:
            return
        await self.bot.db_manager.update_channel(interaction.guild.id, "main_channel_id", canal.id)
        embed = discord.Embed(title="✅ Configuración Actualizada",
                              description=f"El canal principal ha sido establecido en {canal.mention}.",
                              color=discord.Color.green())
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="canal_logs", description="Establece el canal para recibir logs del bot.")
    @app_commands.describe(canal="El canal donde se enviarán los logs.")
    async def set_log_channel(self, interaction: discord.Interaction, canal: discord.TextChannel):
        """Establece el canal donde se enviarán los logs del bot."""
        if not interaction.guild:
            return
        await self.bot.db_manager.update_channel(interaction.guild.id, "log_channel_id", canal.id)
        embed = discord.Embed(title="✅ Configuración Actualizada",
                              description=f"El canal de logs ha sido establecido en {canal.mention}.",
                              color=discord.Color.green())
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="canal_reglas", description="Establece el canal de reglas del servidor.")
    @app_commands.describe(canal="El canal donde están publicadas las reglas.")
    async def set_rules_channel(self, interaction: discord.Interaction, canal: discord.TextChannel):
        """Establece el canal donde se publican las reglas del servidor."""
        if not interaction.guild:
            return
        await self.bot.db_manager.update_channel(interaction.guild.id, "rules_channel_id", canal.id)
        embed = discord.Embed(title="✅ Configuración Actualizada",
                              description=f"El canal de reglas ha sido establecido en {canal.mention}.",
                              color=discord.Color.green())
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="canal_confesiones", description="Establece el canal de confesiones.")
    @app_commands.describe(canal="El canal donde se publican la confesiones anonimas.")
    async def set_confession_channel(self, interaction: discord.Interaction, canal: discord.TextChannel):
        """Establece el canal donde se publican las confesiones anónimas."""
        if not interaction.guild:
            return
        await self.bot.db_manager.update_channel(interaction.guild.id, "confession_channel_id", canal.id)
        embed = discord.Embed(title="✅ Configuración Actualizada",
                              description=f"El canal de confesiones ha sido establecido en {canal.mention}.",
                              color=discord.Color.green())
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="canal_historia", description="Establece el canal para el historial de eventos.")
    @app_commands.describe(canal="El canal donde se enviará el historial de moderación.")
    async def set_history_channel(self, interaction: discord.Interaction, canal: discord.TextChannel):
        """Establece el canal donde se enviará el historial de eventos del servidor."""
        if not interaction.guild:
            return
        await self.bot.db_manager.update_channel(interaction.guild.id, "history_channel_id", canal.id)
        embed = discord.Embed(title="✅ Configuración Actualizada",
                              description=f"El canal de historia ha sido establecido en {canal.mention}.",
                              color=discord.Color.green())
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # COMANDO PARA ACTIVAR/DESACTIVAR FUNCIONES
    @app_commands.command(name="toggle", description="Activa o desactiva una función del bot en este servidor.")
    @app_commands.describe(
        funcion="La función que quieres activar o desactivar.",
        estado="Elige si quieres activar o desactivar la función."
    )
    @app_commands.choices(funcion=[
        app_commands.Choice(name="Logs de Moderación (Historial)", value="history_channel_enabled"),
        app_commands.Choice(name="Mensajes de Bienvenida", value="welcome_message_enabled"),
        app_commands.Choice(name="Tarea 'Feliz Jueves'", value="feliz_jueves_task_enabled"),
        app_commands.Choice(name="Logs de Errores del Bot", value="log_channel_enabled"),
    ])
    async def toggle_feature(self, interaction: discord.Interaction, funcion: app_commands.Choice[str], estado: bool):
        if not interaction.guild:
            return

        await self.bot.db_manager.update_feature_flag(
            interaction.guild.id,
            funcion.value,  # La clave interna de la DB (ej. 'history_channel_enabled')
            estado
        )

        status_text = "✅ Activada" if estado else "❌ Desactivada"

        embed = discord.Embed(
            title="⚙️ Función Actualizada",
            description=f"La función **{funcion.name}** ha sido **{status_text}**.",
            color=discord.Color.green() if estado else discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    """Función para cargar el cog en el bot."""
    await bot.add_cog(Config(bot))