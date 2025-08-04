# app/core/database.py
import logging
import motor.motor_asyncio

from ..schemas.guild_config import get_default_guild_config
from ..schemas.level import get_default_user_level

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

    # --- Configuración de Servidores ---

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

    # --- Experiencia de Usuario ---

    @property
    def user_level_collection(self):
        """
        Devuelve la colección de experiencia de usuario.
        """
        return self.db["user_levels"]

    async def get_user_level(self, guild_id: int, user_id: int):
        """
        Obtiene el documento de experiencia de un usuario en un servidor.
        """
        return await self.user_level_collection.find_one(
            {"guild_id": guild_id, "user_id": user_id}
        )

    async def create_user_level(self, guild_id: int, user_id: int):
        """
        Crea un documento de experiencia por defecto para un usuario en un servidor.
        """
        if await self.get_user_level(guild_id, user_id):
            logger.info(
                f"La experiencia para el usuario {user_id} en el guild {guild_id} ya existe."
            )
            return False
        default_level = get_default_user_level(guild_id, user_id)
        await self.user_level_collection.insert_one(default_level)
        logger.info(
            f"Se ha creado la experiencia inicial para el usuario {user_id} en el guild {guild_id}."
        )
        return True

    async def add_xp(self, guild_id: int, user_id: int, xp: int):
        """
        Añade experiencia a un usuario en un servidor. Si no existe el documento, lo crea.
        """
        user_level = await self.get_user_level(guild_id, user_id)
        if not user_level:
            await self.create_user_level(guild_id, user_id)
        result = await self.user_level_collection.update_one(
            {"guild_id": guild_id, "user_id": user_id},
            {"$inc": {"xp": xp}},
            upsert=True,
        )
        logger.info(f"Añadidos {xp} XP al usuario {user_id} en el guild {guild_id}.")
        return result
