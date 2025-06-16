# app/core/database.py
import logging
import motor.motor_asyncio

from ..schemas.guild_config import get_default_guild_config

logger = logging.getLogger('discord')


class DatabaseManager:
    def __init__(self, mongo_uri: str):
        try:
            self.client = motor.motor_asyncio.AsyncIOMotorClient(mongo_uri)
            self.db = self.client['DiamiBotDB']
            self.collection = self.db['guild_configs']
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
            logger.info(f"La configuración para el Guild {guild_id} ya existe. No se creará una nueva.")
            return False

        default_config = get_default_guild_config(guild_id)

        await self.collection.insert_one(default_config)
        logger.info(f"Se ha creado la configuración inicial para el Guild {guild_id}.")
        return True  # Retornamos True para indicar que se creó una nueva configuración

    async def update_channel(self, guild_id: int, channel_type: str, channel_id: int):
        """
        Actualiza un campo de canal específico en la configuración de un servidor.
        Si la configuración del servidor no existe, la crea primero (operación 'upsert' lógica).

        Args:
            guild_id (int): El ID del servidor.
            channel_type (str): La clave del campo a actualizar (ej. 'main_channel_id').
            channel_id (int): El nuevo ID del canal.
        """
        default_values = get_default_guild_config(guild_id)
        # Eliminamos el _id porque no debe estar en el operador $setOnInsert
        del default_values["_id"]

        await self.collection.update_one(
            {"_id": guild_id},
            {
                "$set": {channel_type: channel_id},
                "$setOnInsert": default_values
            },
            upsert=True
        )
        logger.info(f"Guild {guild_id}: Se actualizó '{channel_type}' a {channel_id}.")

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
            upsert=True  # Si el documento no existe, se creará con esta actualización
        )
        logger.info(f"Guild {guild_id}: Flag '{feature_name}' establecido a {status}.")
