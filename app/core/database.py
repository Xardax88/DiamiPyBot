# app/core/database.py
import logging
import motor.motor_asyncio

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
            return False  # Retornamos False para indicar que no se creó nada nuevo

        default_config = {
            "_id": guild_id,
            "main_channel_id": None,
            "log_channel_id": None,
            "rules_channel_id": None,
        }
        await self.collection.insert_one(default_config)
        logger.info(f"Se ha creado la configuración inicial para el Guild {guild_id}.")
        return True  # Retornamos True para indicar que se creó una nueva configuración

    # --- MÉTODO MODIFICADO ---
    async def update_channel(self, guild_id: int, channel_type: str, channel_id: int):
        """
        Actualiza un campo de canal específico en la configuración de un servidor.
        Si la configuración del servidor no existe, la crea primero (operación 'upsert' lógica).

        Args:
            guild_id (int): El ID del servidor.
            channel_type (str): La clave del campo a actualizar (ej. 'main_channel_id').
            channel_id (int): El nuevo ID del canal.
        """
        # Primero, verificamos si la configuración del guild existe.
        config = await self.get_guild_config(guild_id)

        # Si no existe, la creamos.
        if not config:
            logger.warning(
                f"No se encontró configuración para Guild {guild_id}. Creando una nueva antes de actualizar.")
            await self.create_guild_config(guild_id)

        # Ahora que estamos seguros de que existe, realizamos la actualización.
        await self.collection.update_one(
            {"_id": guild_id},
            {"$set": {channel_type: channel_id}}
        )
        logger.info(f"Guild {guild_id}: Se actualizó '{channel_type}' a {channel_id}.")