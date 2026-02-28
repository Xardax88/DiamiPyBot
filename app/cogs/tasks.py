# app/cogs/tasks.py
import logging
import datetime
import random

import discord
from discord.ext import commands, tasks

logger = logging.getLogger(__name__)

# ==============================================================================
# Define la zona horaria para GMT-3 (Argentina)
# ==============================================================================
GMT_MINUS_3 = datetime.timezone(datetime.timedelta(hours=-3))

# ==============================================================================
# Lista de mensajes para el "Feliz Jueves"
# ==============================================================================
MENSAJES_JUEVES = [
    "Feliz Jueves. Mitad de semana superada, *fírimar*. Ya casi es viernes. ☕",
    "Tomen, para que no decaiga el ánimo. Feliz Jueves.",
    "Ai... un día más cerca del fin de semana. No se rindan.",
    "Para ustedes, mortales que necesitan un empujón a mitad de semana. Feliz Jueves! 🤘",
    "Feliz Jueves. Ahora, si me disculpan, mi café me espera.",
]


# ==============================================================================
# Cog para manejar tareas programadas
# ==============================================================================
class ScheduledTasks(commands.Cog, name="tasks"):
    """
    Un cog para manejar todas las tareas programadas que no dependen directamente de la IA,
    como eventos semanales o recordatorios.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.last_jueves_sent = None
        self.feliz_jueves_task.start()

    def cog_unload(self):
        """Asegura que la tarea se detenga si el cog se descarga."""
        self.feliz_jueves_task.cancel()

    @tasks.loop(time=datetime.time(hour=8, minute=0, tzinfo=GMT_MINUS_3))
    async def feliz_jueves_task(self):
        """
        Tarea que se ejecuta cada cinco horas para comprobar si es el momento de enviar
        el meme de "Feliz Jueves".
        """

        # Obtiene la fecha actual en la zona horaria para saber si es jueves.
        today_in_gmt_minus_3 = datetime.datetime.now(GMT_MINUS_3).date()

        # Solo se ejecuta si es jueves (0=Lunes, 3=Jueves)
        if today_in_gmt_minus_3.weekday() != 3:
            return

        logger.info("¡Es Jueves! Preparando el envío del meme.")

        # Buscamos en todos los servidores el canal principal para enviar el meme
        for guild in self.bot.guilds:
            try:
                # Accedemos al db_manager a través del bot
                config = await self.bot.db_manager.get_guild_config(guild.id)
                if not config or not config.get("main_channel_id"):
                    # Si no hay configuración o el canal principal no está definido, saltamos al siguiente servidor
                    continue
                if not config.get("features", {}).get(
                    "feliz_jueves_task_enabled", False
                ):
                    # Si la tarea no está habilitada, saltamos al siguiente servidor
                    continue

                channel_id = config.get("main_channel_id")
                channel = guild.get_channel(channel_id)

                if channel and isinstance(channel, discord.TextChannel):
                    image_path = "assets/images/feliz-jueves.png"
                    try:
                        file = discord.File(image_path, filename="feliz-jueves.png")
                        # Elegir un mensaje aleatorio de la lista
                        message_text = random.choice(MENSAJES_JUEVES)

                        await channel.send(content=message_text, file=file)
                        logger.info(
                            f"Meme 'Feliz Jueves' enviado en el servidor '{guild.name}'.",
                            extra={"guild_id": guild.id},
                        )

                    except FileNotFoundError:
                        logger.error(
                            f"No se encontró el archivo del meme 'feliz_jueves.png' en la ruta: {image_path}",
                            extra={"guild_id": guild.id},
                        )
                    except Exception as e:
                        logger.error(
                            f"Error al enviar el meme en '{guild.name}': {e}",
                            extra={"guild_id": guild.id},
                        )

            except Exception as e:
                logger.error(
                    f"Error procesando el servidor {guild.name} para la tarea de Feliz Jueves: {e}",
                    extra={"guild_id": guild.id},
                )

    @feliz_jueves_task.before_loop
    async def before_feliz_jueves_task(self):
        """Espera a que el bot esté listo antes de iniciar la tarea."""
        await self.bot.wait_until_ready()


# ==============================================================================
# FUNCIÓN DE CARGA DEL COG
# ==============================================================================
async def setup(bot: commands.Bot):
    """Función para cargar el cog en el bot."""
    await bot.add_cog(ScheduledTasks(bot))
