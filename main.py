#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Diami Bot - Edición Python

Este archivo es el punto de entrada principal para el bot de Discord "Diami".
Se encarga de las siguientes tareas:
1. Cargar las variables de entorno desde el archivo .env.
2. Configurar el sistema de logging para la consola y los archivos.
3. Instanciar la clase principal del bot (Diami).
4. Iniciar la conexión del bot con la API de Discord.

Project: DiamiPyBot
Author: Xardax (Maximiliano Paragoni)

Copyright (c) 2025-presente, Xardax (Maximiliano Paragoni)
Licenciado bajo la Licencia MIT.
"""

import os
import logging
import asyncio
from dotenv import load_dotenv

from app import Diami


def setup_logging():
    """Configura el sistema de logging."""

    if not os.path.exists("logs"):
        os.makedirs("logs")

    logger = logging.getLogger("discord")
    logger.setLevel(logging.DEBUG)
    logging.getLogger().setLevel(logging.INFO)

    file_handler = logging.FileHandler(
        filename="logs/diami.log", encoding="utf-8", mode="w"
    )
    file_formatter = logging.Formatter(
        "%(asctime)s:%(levelname)s:%(name)s: %(message)s"
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter("%(name)-12s: %(levelname)-8s %(message)s")
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)

    logging.getLogger().addHandler(file_handler)
    logging.getLogger().addHandler(console_handler)


async def main():
    """Función principal para configurar y ejecutar el bot."""
    setup_logging()
    load_dotenv()

    TOKEN = os.getenv("DISCORD_TOKEN")
    MONGO_URI = os.getenv("MONGO_URI")
    GUILD_ID_STR = os.getenv("GUILD_ID")

    if not TOKEN:
        logging.critical("¡ERROR! DISCORD_TOKEN no encontrado en .env")
        return

    if not TOKEN or not MONGO_URI:
        logging.critical(
            "¡ERROR CRÍTICO! DISCORD_TOKEN o MONGO_URI no se encontraron en el archivo .env"
        )
        return

    guild_id = int(GUILD_ID_STR) if GUILD_ID_STR and GUILD_ID_STR.isdigit() else None

    bot = Diami(mongo_uri=MONGO_URI, guild_id=guild_id)

    async with bot:
        await bot.start(TOKEN)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot detenido por el usuario.")
