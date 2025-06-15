# app/core/logging_handler.py
import logging
import asyncio
import discord


class LoggingHandler(logging.Handler):
    """
    Un handler de logging que envía los registros a un canal de Discord específico.
    Usa una cola y una tarea en segundo plano para evitar el bloqueo del bot y el rate-limiting.
    """

    def __init__(self, bot: discord.Client, channel_id: int):
        super().__init__()
        self.bot = bot
        self.channel_id = channel_id
        self.queue = asyncio.Queue()
        self.task = asyncio.create_task(self._log_sender())

    async def _log_sender(self):
        """Tarea en segundo plano que consume de la cola y envía los logs."""
        await self.bot.wait_until_ready()
        channel = self.bot.get_channel(self.channel_id)
        if not channel:
            print(f"ERROR DE LOGGING: No se pudo encontrar el canal de log con ID {self.channel_id}.")
            return

        while not self.bot.is_closed():
            try:
                log_record = await self.queue.get()
                if log_record is None:  # Señal para terminar
                    break

                log_message = self.format(log_record)

                # Para evitar exceder el límite de caracteres de Discord, dividimos mensajes largos
                for chunk in self._split_message(log_message):
                    await channel.send(chunk)
                    await asyncio.sleep(1.1)  # Pequeña espera para evitar rate-limits
            except Exception as e:
                # Si el envío de logs falla, lo imprimimos en la consola
                print(f"Error crítico en el LoggingHandler: {e}")

    def _split_message(self, message: str, chunk_size: int = 1990) -> list[str]:
        """Divide un mensaje largo en trozos más pequeños."""
        if len(message) <= chunk_size:
            return [f"```{message}```"]  # Envolvemos en bloque de código

        return [f"```{message[i:i + chunk_size]}```" for i in range(0, len(message), chunk_size)]

    def emit(self, record: logging.LogRecord):
        """
        Este método es llamado por el sistema de logging.
        En lugar de enviar directamente, pone el registro en la cola.
        """
        # Formateamos el registro aquí para que la tarea no tenga que hacerlo
        # y evitamos pasar objetos complejos a través de la cola de asyncio.
        # No usamos self.format, ya que se hará en _log_sender,
        # simplemente ponemos el record en la cola.
        self.queue.put_nowait(record)

    def close(self):
        """Cierra el handler y la tarea en segundo plano de forma segura."""
        self.queue.put_nowait(None)
        # Podríamos esperar a que la tarea termine, pero para un bot,
        # a menudo simplemente la cancelamos al cerrar.
        self.task.cancel()
        super().close()