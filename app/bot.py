#bot.py
import os
import logging
from typing import Optional

import discord
from discord.ext import commands

from .core.database import DatabaseManager

# Creamos un logger específico para nuestro bot
logger = logging.getLogger('discord')

class Diami(commands.Bot):
    """
    Clase principal para el bot Diami.
    Hereda de commands.Bot para toda la funcionalidad básica.
    """
    def __init__(self, mongo_uri: str, guild_id: Optional[int] = None):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True

        super().__init__(command_prefix=">", intents=intents)

        self.guild_id = guild_id
        self.db_manager = DatabaseManager(mongo_uri)

        logger.info(f"Bot Diami inicializado. Guild de sincronización: {self.guild_id or 'Global'}")

    async def on_guild_join(self, guild: discord.Guild):
        logger.info(f"¡El bot ha sido añadido al servidor: {guild.name} (ID: {guild.id})!")
        await self.db_manager.create_guild_config(guild.id)

    async def on_ready(self):

        logger.info(f'Conectado como {self.user} (ID: {self.user.id})')
        logger.info('------')
        print(f'Bot {self.user} está en línea y listo.')

    async def setup_hook(self):

        logger.info("--- Cargando Cogs ---")
        # Buscamos todos los archivos .py en la carpeta 'cogs'
        cogs_path = 'app.cogs'
        for filename in os.listdir('./app/cogs'):
            if filename.endswith('.py')  and not filename.startswith('__'):
                cog_name = f"{cogs_path}.{filename[:-3]}"
                try:
                    await self.load_extension(cog_name)
                    logger.info(f'Se cargó el cog: {cog_name}')
                except Exception as e:
                    logger.error(f'Falló la carga del cog {cog_name}. Error: {e}')

        # --- Sincronización de Comandos Slash ---

        if self.guild_id:
            guild = discord.Object(id=self.guild_id)
            # Copiamos los comandos globales al árbol del guild
            self.tree.copy_global_to(guild=guild)
            # Sincronizamos el árbol de comandos con el guild específico
            await self.tree.sync(guild=guild)
            logger.info(f"Comandos slash sincronizados con el Guild ID: {self.guild_id}")
        else:
            # Si no hay GUILD_ID, sincronizamos globalmente.
            # Puede tardar hasta una hora en reflejarse en todos los servidores.
            await self.tree.sync()
            logger.info("Comandos slash sincronizados globalmente.")