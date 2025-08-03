# app/core/logging_handler.py
import logging
import asyncio
import discord


class LoggingHandler(logging.Handler):
    """
    Handler de logging que envía los registros a los canales de log de cada servidor (guild) en Discord.
    Utiliza una cola y una tarea asíncrona para evitar bloqueos y rate-limiting.
    El canal de log se determina dinámicamente según el guild_id incluido en el log.
    """

    def __init__(self, bot: discord.Client, db_manager, default_channel_id: int = None):
        """
        Args:
            bot (discord.Client): Instancia del bot de Discord.
            db_manager (DatabaseManager): Gestor de base de datos para obtener el canal de log de cada guild.
            default_channel_id (int, opcional): Canal de log por defecto si no se especifica guild_id.
        """
        super().__init__()
        self.bot = bot
        self.db_manager = db_manager
        self.default_channel_id = default_channel_id
        self.queue = asyncio.Queue()
        self.task = asyncio.create_task(self._log_sender())

    async def _get_log_channel(self, guild_id: int = None):
        """
        Obtiene el canal de log para un guild específico desde la base de datos.
        Si no se encuentra, retorna el canal por defecto (si está definido).
        """
        if guild_id is not None:
            config = await self.db_manager.get_guild_config(guild_id)
            if config and "log_channel_id" in config:
                channel = self.bot.get_channel(config["log_channel_id"])
                if channel:
                    return channel
        # Si no hay guild_id o no se encuentra el canal, usar el canal por defecto
        if self.default_channel_id:
            return self.bot.get_channel(self.default_channel_id)
        return None

    async def _log_sender(self):
        """
        Tarea en segundo plano que consume la cola y envía los logs al canal adecuado.
        Solo envía logs a Discord si tienen guild_id. Si no, los logs se procesan por los otros handlers (consola, archivo, etc.).
        """
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            try:
                log_record = await self.queue.get()
                if log_record is None:
                    break
                # Extraemos guild_id del log si existe
                guild_id = getattr(log_record, "guild_id", None)
                if guild_id is None:
                    # No enviar a Discord, solo dejar que otros handlers lo manejen
                    continue
                channel = await self._get_log_channel(guild_id)
                if not channel:
                    # No se encontró canal de log para este guild, omitir
                    continue
                log_message = self.format(log_record)
                for chunk in self._split_message(log_message):
                    await channel.send(chunk)
                    await asyncio.sleep(1.1)
            except Exception as e:
                print(f"Error crítico en el LoggingHandler: {e}")

    def _split_message(self, message: str, chunk_size: int = 1990) -> list[str]:
        """Divide un mensaje largo en trozos más pequeños."""
        if len(message) <= chunk_size:
            return [f"```{message}```"]  # Envolvemos en bloque de código

        return [
            f"```{message[i:i + chunk_size]}```"
            for i in range(0, len(message), chunk_size)
        ]

    def emit(self, record: logging.LogRecord):
        """
        Este método es llamado por el sistema de logging.
        En lugar de enviar directamente, pone el registro en la cola.
        Para logs por guild, se recomienda usar: logger.info(msg, extra={"guild_id": id})
        """
        self.queue.put_nowait(record)

    def close(self):
        """Cierra el handler y la tarea en segundo plano de forma segura."""
        self.queue.put_nowait(None)
        # Podríamos esperar a que la tarea termine, pero para un bot,
        # a menudo simplemente la cancelamos al cerrar.
        self.task.cancel()
        super().close()
