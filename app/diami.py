# diami.py
import os
import logging
from typing import Optional

import discord
from discord.ext import commands

from .core.database import DatabaseManager

from app.core.logging_handler import LoggingHandler

# Creamos un logger específico para nuestro bot
logger = logging.getLogger("discord")


# ==============================================================================
# Clase principal del bot Diami
# ==============================================================================
class Diami(commands.Bot):
    """
    Clase principal para el bot Diami.
    """

    def __init__(self, mongo_uri: str, guild_id: Optional[int] = None):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.members = True

        super().__init__(command_prefix=">", intents=intents)

        self.guild_id = guild_id
        self.db_manager = DatabaseManager(mongo_uri)

        logger.info(
            f"Diami inicializado. Guild de sincronización: {self.guild_id or 'Global'}"
        )

    async def on_guild_join(self, guild: discord.Guild):
        logger.info(
            f"¡El bot ha sido añadido al servidor: {guild.name} (ID: {guild.id})!"
        )
        await self.db_manager.create_guild_config(guild.id)

    async def on_ready(self):

        logger.info(f"Conectado como {self.user} (ID: {self.user.id})")

        await self.change_presence(
            activity=discord.CustomActivity(
                name="🐍 Lista para matar a dios, o convertirme en el!",
            ),
        )
        print(f"{self.user} está en línea y lista.")

    async def setup_hook(self):
        """El hook para cargar cogs y sincronizar comandos."""

        # Configuración del DiscordLoggingHandler
        try:
            root_logger = logging.getLogger()
            # Crea y añade handler personalizado que usa db_manager y soporta logs por guild
            discord_handler = LoggingHandler(bot=self, db_manager=self.db_manager)
            # Establece un formato para los logs de Discord
            formatter = logging.Formatter("%(levelname)s - %(name)s - %(message)s")
            discord_handler.setFormatter(formatter)
            # Establece el nivel. Por ejemplo, INFO y superior.
            discord_handler.setLevel(logging.INFO)
            root_logger.addHandler(discord_handler)
            logging.info(f"LoggingHandler configurado para logs por guild.")
        except Exception as e:
            logging.error(f"Error al configurar el LoggingHandler: {e}", exc_info=True)

        # --- Sincronización de Comandos Slash ---

        logger.info("--- Cargando Cogs ---")
        # Busca todos los archivos .py en la carpeta 'cogs'
        cogs_path = "app.cogs"
        for filename in os.listdir("./app/cogs"):
            if filename.endswith(".py") and not filename.startswith("__"):
                cog_name = f"{cogs_path}.{filename[:-3]}"
                try:
                    await self.load_extension(cog_name)
                    logger.info(f"Se cargó el cog: {cog_name}")
                except Exception as e:
                    logger.error(f"Falló la carga del cog {cog_name}. Error: {e}")

        if self.guild_id:
            guild = discord.Object(id=self.guild_id)
            # Copia los comandos globales al árbol del guild
            self.tree.copy_global_to(guild=guild)
            # Sincroniza el árbol de comandos con el guild específico
            await self.tree.sync(guild=guild)
            logger.info(
                f"Comandos slash sincronizados con el Guild ID: {self.guild_id}"
            )
        else:
            # Si no hay GUILD_ID, sincroniza globalmente.
            await self.tree.sync()
            logger.info("Comandos slash sincronizados globalmente.")
