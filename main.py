#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ==============================================================================
# main.py
# ------------------------------------------------------------------------------
# Punto de entrada principal para el bot de Discord "Diami" (Edición Python).
# - Carga variables de entorno y configura logging.
# - Instancia y ejecuta el bot principal (Diami).
#
# Autor: Xardax (Maximiliano Paragoni)
# Proyecto: DiamiPyBot
# Fecha: 2025
# Licencia: MIT
# ==============================================================================

import os
import logging
import asyncio
from dotenv import load_dotenv
from app import Diami


# -----------------------------------------------------------------------
# Carga de variables de entorno
# -----------------------------------------------------------------------
class ConfigLoader:
    """Carga y valida la configuración desde variables de entorno."""

    def __init__(self, env_file: str = ".env"):
        load_dotenv(env_file, override=False)
        self.token = os.getenv("DISCORD_TOKEN")
        self.mongo_uri = os.getenv("MONGO_URI")
        self.guild_id = self._parse_guild_id(os.getenv("GUILD_ID"))
        self.session_secret = os.getenv("SESSION_SECRET_KEY")

    @staticmethod
    def _parse_guild_id(guild_id_str):
        return int(guild_id_str) if guild_id_str and guild_id_str.isdigit() else None

    def validate(self):
        if not self.token:
            raise ValueError("¡ERROR! DISCORD_TOKEN no encontrado en .env")
        if not self.mongo_uri:
            raise ValueError("¡ERROR! MONGO_URI no encontrado en .env")


# -----------------------------------------------------------------------
# Configuración del sistema de logging
# -----------------------------------------------------------------------
class LoggerConfigurator:
    """Configura el sistema de logging."""

    @staticmethod
    def setup(log_dir="logs", log_file="diami.log"):
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        logger = logging.getLogger("discord")
        logger.setLevel(logging.DEBUG)
        logging.getLogger().setLevel(logging.INFO)

        file_handler = logging.FileHandler(
            filename=os.path.join(log_dir, log_file), encoding="utf-8", mode="w"
        )
        file_formatter = logging.Formatter(
            "%(asctime)s:%(levelname)s:%(name)s: %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            "%(name)-12s: %(levelname)-8s %(message)s"
        )
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(logging.INFO)

        logging.getLogger().addHandler(file_handler)
        logging.getLogger().addHandler(console_handler)


# -----------------------------------------------------------------------
# Clase principal del bot
# -----------------------------------------------------------------------
class BotRunner:
    """Inicialización y ejecución del bot."""

    def __init__(self, config: ConfigLoader):
        self.config = config

    async def run(self):
        self.config.validate()
        bot = Diami(mongo_uri=self.config.mongo_uri, guild_id=self.config.guild_id)
        async with bot:
            await bot.start(self.config.token)


# -----------------------------------------------------------------------
# Función principal
# -----------------------------------------------------------------------
def main():
    LoggerConfigurator.setup()
    config = ConfigLoader()
    runner = BotRunner(config)
    try:
        asyncio.run(runner.run())
    except ValueError as e:
        logging.critical(str(e))
    except KeyboardInterrupt:
        logging.info("Bot detenido por el usuario.")


if __name__ == "__main__":
    main()
