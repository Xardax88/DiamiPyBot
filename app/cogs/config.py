# app/cogs/config.py
import logging
import discord
from discord import app_commands
from discord.ext import commands

logger = logging.getLogger(__name__)


# ==============================================================================
# Sub-Grupo para /config set
# ==============================================================================
class SetGroup(app_commands.Group):
    # Heredamos de app_commands.Group, no de commands.GroupCog
    def __init__(self, bot: commands.Bot):
        # El nombre del grupo se define en el decorador de la clase padre
        super().__init__(
            name="set", description="Configura diferentes aspectos del bot."
        )
        self.bot = bot

    @app_commands.command(
        name="channel", description="Establece un canal para una función específica."
    )
    @app_commands.describe(
        tipo="El tipo de canal que quieres configurar.",
        canal="El canal de texto que quieres asignar.",
    )
    @app_commands.choices(
        tipo=[
            app_commands.Choice(name="Principal", value="main_channel_id"),
            app_commands.Choice(name="Logs", value="log_channel_id"),
            app_commands.Choice(name="Reglas", value="rules_channel_id"),
            app_commands.Choice(name="Historial", value="history_channel_id"),
            app_commands.Choice(name="Confesiones", value="confession_channel_id"),
            app_commands.Choice(name="Reportes", value="report_channel_id"),
            app_commands.Choice(name="Sugerencias", value="suggestion_channel_id"),
        ]
    )
    async def set_channel(
        self,
        interaction: discord.Interaction,
        tipo: app_commands.Choice[str],
        canal: discord.TextChannel,
    ):
        if not interaction.guild:
            return
        logger.info(
            f"channel {canal.id}, tipo {tipo.value}, guild {interaction.guild.id}"
        )
        await self.bot.db_manager.update_channel(
            interaction.guild.id, tipo.value, canal.id
        )
        embed = discord.Embed(
            title="✅ Canal Configurado",
            description=f"El canal de **{tipo.name}** ha sido establecido en {canal.mention}.",
            color=discord.Color.green(),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name="feature", description="Activa o desactiva una función del bot."
    )
    @app_commands.describe(
        funcion="La función que quieres activar o desactivar.",
        estado="Elige si quieres activar o desactivar la función.",
    )
    @app_commands.choices(
        funcion=[
            app_commands.Choice(
                name="Logs de Moderación (Historial)", value="history_channel_enabled"
            ),
            app_commands.Choice(
                name="Mensajes de Bienvenida", value="welcome_message_enabled"
            ),
            app_commands.Choice(
                name="Tarea 'Feliz Jueves'", value="feliz_jueves_task_enabled"
            ),
            app_commands.Choice(
                name="Logs de Errores del Bot", value="log_channel_enabled"
            ),
        ]
    )
    async def set_feature_status(
        self,
        interaction: discord.Interaction,
        funcion: app_commands.Choice[str],
        estado: bool,
    ):
        if not interaction.guild:
            return
        await self.bot.db_manager.update_feature_flag(
            interaction.guild.id, funcion.value, estado
        )
        status_text = "✅ Activada" if estado else "❌ Desactivada"
        embed = discord.Embed(
            title="⚙️ Función Actualizada",
            description=f"La función **{funcion.name}** ha sido **{status_text}**.",
            color=discord.Color.green() if estado else discord.Color.red(),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


# ==============================================================================
# Sub-Grupo para /config status
# ==============================================================================
class StatusGroup(app_commands.Group):
    def __init__(self, bot: commands.Bot):
        super().__init__(
            name="status", description="Muestra el estado de la configuración del bot."
        )
        self.bot = bot

    @app_commands.command(
        name="all",
        description="Muestra la configuración completa del bot para este servidor.",
    )
    async def view_all_config(self, interaction: discord.Interaction):
        if not interaction.guild:
            return
        await interaction.response.defer(ephemeral=True)
        config = await self.bot.db_manager.get_guild_config(interaction.guild.id)
        embed = discord.Embed(
            title=f"⚙️ Estado de Configuración de {interaction.guild.name}",
            color=discord.Color.blue(),
        )
        if not config:
            embed.description = (
                "No hay ninguna configuración guardada para este servidor."
            )
            await interaction.followup.send(embed=embed)
            return

        channel_map = {
            "main_channel_id": "Principal",
            "log_channel_id": "Logs",
            "rules_channel_id": "Reglas",
            "history_channel_id": "Historia",
            "confession_channel_id": "Confesiones",
            "report_channel_id": "Canal de Reportes",
            "suggestion_channel_id": "Sugerencias",
        }
        channel_text = ""
        for key, name in channel_map.items():
            channel_id = config.get(key)
            value = "❌ *Sin configurar*"
            if channel_id:
                channel = interaction.guild.get_channel(channel_id)
                value = channel.mention if channel else f"⚠️ *Canal no encontrado*"
            channel_text += f"**{name}:** {value}\n"
        embed.add_field(name="Canales Configurados", value=channel_text, inline=False)

        feature_map = {
            "history_channel_enabled": "Moderación",
            "welcome_message_enabled": "Bienvenida",
            "feliz_jueves_task_enabled": "'Feliz Jueves'",
            "log_channel_enabled": "Logs de Errores",
        }

        feature_text = ""
        features = config.get("features", {})
        for key, name in feature_map.items():
            status = features.get(key, False)
            status_emoji = "✅ Activado" if status else "❌ Desactivado"
            feature_text += f"**{name}:** {status_emoji}\n"
        embed.add_field(
            name="Estado de las Funciones", value=feature_text, inline=False
        )

        await interaction.followup.send(embed=embed)


# ==============================================================================
# Cog Principal que agrupa los sub-grupos
# ==============================================================================
@app_commands.default_permissions(administrator=True)
class Config(commands.Cog):
    # El GroupCog ahora actúa como un contenedor para los otros grupos
    config_group = app_commands.Group(
        name="config", description="Comandos para configurar el bot."
    )

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Añadimos los grupos de comandos al árbol de comandos del bot
        # a través del Cog.
        self.config_group.add_command(SetGroup(bot))
        self.config_group.add_command(StatusGroup(bot))
        #self.bot.tree.add_command(
        #    self.config_group,
        #    guild=discord.Object(id=bot.guild_id) if bot.guild_id else None,
        #)

    # Este método es importante para cuando el cog se descarga (unload)
    def cog_unload(self):
        self.bot.tree.remove_command(
            self.config_group.name,
            guild=discord.Object(id=self.bot.guild_id) if self.bot.guild_id else None,
        )


# ==============================================================================
# Función de Carga del Cog
# ==============================================================================
async def setup(bot: commands.Bot):
    """Función para cargar el cog principal y sus sub-grupos."""
    await bot.add_cog(Config(bot))
