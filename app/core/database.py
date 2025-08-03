# app/core/database.py
import logging
import motor.motor_asyncio

from ..schemas.guild_config import get_default_guild_config

logger = logging.getLogger("discord")


class DatabaseManager:
    def __init__(self, mongo_uri: str):
        try:
            self.client = motor.motor_asyncio.AsyncIOMotorClient(mongo_uri)
            self.db = self.client["DiamiBotDB"]
            self.collection = self.db["guild_configs"]
            logger.info("Conexión con MongoDB establecida exitosamente.")
        except Exception as e:
            logger.critical(f"No se pudo conectar a MongoDB: {e}")
            self.client = None

    async def get_guild_config(self, guild_id: int):
        """Obtiene la configuración de un servidor específico por su ID."""
        return await self.collection.find_one({"_id": guild_id})

    async def create_guild_config(self, guild_id: int):
        """
        Crea un documento de configuración por defecto para un nuevo servidor.
        Se ejecuta cuando el bot se une a un nuevo guild.
        """
        if await self.get_guild_config(guild_id):
            logger.info(
                f"La configuración para el Guild {guild_id} ya existe. No se creará una nueva."
            )
            return False

        default_config = get_default_guild_config(guild_id)

        await self.collection.insert_one(default_config)
        logger.info(f"Se ha creado la configuración inicial para el Guild {guild_id}.")
        return True  # Retornamos True para indicar que se creó una nueva configuración

    async def ensure_guild_config(self, guild_id: int):
        """
        Verifica si el documento de configuración del servidor existe en la base de datos.
        Si no existe, lo crea con los valores por defecto.
        """
        config = await self.get_guild_config(guild_id)
        if not config:
            await self.create_guild_config(guild_id)
            logger.info(
                f"Configuración creada automáticamente para el Guild {guild_id}."
            )
        else:
            logger.info(f"Configuración ya existe para el Guild {guild_id}.")
        return await self.get_guild_config(guild_id)

    async def update_channel(self, guild_id: int, channel_type: str, channel_id: int):
        """
        Actualiza un campo de canal específico en la configuración de un servidor.
        Si el campo existe como objeto, lo elimina antes de actualizar para evitar conflictos de tipo en MongoDB.
        Si el documento no existe, lo crea primero.
        """
        logger.info(
            f"Actualizando canal {channel_type} para el Guild {guild_id} con ID {channel_id}."
        )
        await self.collection.update_one(
            {"_id": guild_id},
            {"$set": {channel_type: channel_id}},
            upsert=True,  # Si el documento no existe, se creará con esta actualización
        )

    async def update_feature_flag(self, guild_id: int, feature_name: str, status: bool):
        """
        Activa o desactiva una función específica para un servidor.

        Args:
            guild_id (int): El ID del servidor.
            feature_name (str): La clave de la función (ej. 'history_channel_enabled').
            status (bool): True para activar, False para desactivar.
        """
        # Usamos la notación de punto para actualizar un campo en un documento anidado.
        update_key = f"features.{feature_name}"

        await self.collection.update_one(
            {"_id": guild_id},
            {"$set": {update_key: status}},
            upsert=True,  # Si el documento no existe, se creará con esta actualización
        )
        logger.info(f"Guild {guild_id}: Flag '{feature_name}' establecido a {status}.")
