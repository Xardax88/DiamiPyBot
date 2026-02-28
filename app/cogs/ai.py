# app/cogs/ai.py
import os
import logging
import asyncio
from datetime import datetime
from io import BytesIO
import random
from zoneinfo import ZoneInfo

import discord
from discord.ext import commands, tasks
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from PIL import Image

logger = logging.getLogger(__name__)

# ==============================================================================
# Lista de saludos comunes
# ==============================================================================
SALUDOS_COMUNES = [
    "hola",
    "buenas",
    "buenos dias",
    "buenas tardes",
    "buenas noches",
    "buen dia",
    "que tal",
    "como andan",
    "todo bien",
    "holis",
    "hey",
    "que onda",
    "saludos",
    "hi",
    "hello",
    "saludos a todos",
    "morning",
]

# ==============================================================================
# Configuración del modelo de Gemini
# ==============================================================================
MODEL = "gemini-2.0-flash-lite"  # Modelo de Gemini a utilizar
PROMPT_PATH = "data/prompts/personality.md"
ARGENTINA_TZ = ZoneInfo("America/Argentina/Buenos_Aires")
WEEKDAYS_ES = [
    "Lunes",
    "Martes",
    "Miércoles",
    "Jueves",
    "Viernes",
    "Sábado",
    "Domingo",
]


# ==============================================================================
# Inteligencia Artificial Diami
# ==============================================================================
class AI(commands.Cog, name="Inteligencia Artificial Diami"):
    """
    Cog dedicado a la IA, Diami. Gestiona su personalidad, interacciones reactivas y proactivas.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.critical("¡LA CLAVE DE API DE GEMINI NO ESTÁ CONFIGURADA!")
            raise ValueError("GEMINI_API_KEY no encontrada en el archivo .env")

        genai.configure(api_key=api_key)

        self.generation_config = genai.GenerationConfig(
            temperature=0.7,  # Temperatura para respuestas más creativas
            max_output_tokens=1024,  # Límite de tokens para la respuesta
            top_p=0.95,  # Top-p sampling para mayor diversidad
            top_k=40,  # Top-k sampling para limitar el número de opciones
        )
        # Bloquea contenido que tiene una probabilidad media o alta de ser peligroso.
        # Puedes ajustarlo a BLOCK_ONLY_HIGH, BLOCK_LOW_AND_ABOVE, o BLOCK_NONE.
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }

        self.model = genai.GenerativeModel(
            model_name=MODEL,
            generation_config=self.generation_config,
            safety_settings=self.safety_settings,
        )
        logger.info(f"Modelo de Gemini {MODEL} inicializado.")

        self.personality_prompt = self._load_personality_prompt()
        if not self.personality_prompt:
            logger.critical(
                "El prompt de personalidad no se pudo cargar. La IA no funcionará correctamente."
            )

        # Inicia la tarea proactiva que permite a Diami unirse a conversaciones de forma autónoma.
        self.proactive_conversation_task.start()

    def cog_unload(self):
        """Asegura que la tarea se detenga si el cog se descarga."""
        self.proactive_conversation_task.cancel()

    def _load_personality_prompt(self) -> str | None:
        try:
            with open(PROMPT_PATH, "r", encoding="utf-8") as prompt_file:
                content = prompt_file.read().strip()
            logger.info("Prompt de personalidad cargado exitosamente desde Markdown.")
            return content
        except Exception as e:
            logger.error(
                f"Error al cargar el archivo de personalidad: {e}", exc_info=True
            )
            return None

    def _get_current_timestamp(self) -> str:
        now = datetime.now(ARGENTINA_TZ)
        weekday_es = WEEKDAYS_ES[now.weekday()]
        return (
            f"<timestamp_actual>{weekday_es}, {now.strftime('%d/%m/%Y %H:%M')} "
            "(UTC-3)</timestamp_actual>"
        )

    async def _get_message_history_xml(
        self,
        channel: discord.TextChannel,
        limit: int = 40,
        max_chars: int = 3000,
    ) -> str:

        history_parts = []
        current_chars = 0
        async for old_message in channel.history(limit=limit, oldest_first=True):
            if not old_message.content and not old_message.attachments:
                continue

            content = discord.utils.escape_markdown(old_message.content)
            content = discord.utils.escape_mentions(content)
            content = " ".join(content.split())

            if len(content) > 220:
                content = f"{content[:217]}..."

            if old_message.attachments:
                content += f" [Adjuntó {len(old_message.attachments)} imagen(es)]"

            line = f"{old_message.author.display_name}: {content.strip()}"
            if not line.strip():
                continue

            projected_chars = current_chars + len(line) + 1
            if projected_chars > max_chars:
                break

            history_parts.append(line)
            current_chars = projected_chars

        history_str = "\n".join(history_parts)
        return f"<historial_chat>\n{history_str}\n</historial_chat>"

    async def _generate_gemini_response(
        self,
        channel: discord.TextChannel,
        user_name: str,
        user_input: str,
        attachments: list | None = None,
    ):
        """
        Genera una respuesta usando Gemini, diferenciando entre prompts normales y comandos internos.
        Si el prompt inicia con '>>command>>', se prioriza la tarea y se omite el contexto de canal.
        """
        prompt_parts = [self.personality_prompt]
        # Detectar si es un comando interno
        if user_input.strip().startswith(">>command>>"):
            # Solo se envía el prompt de personalidad y el comando, sin contexto adicional
            prompt_parts.append(user_input)
            # Las imágenes no se envían en comandos internos
        else:
            # Prompt normal: agregar contexto de canal, historial y timestamp
            if channel is not None:
                history_xml = await self._get_message_history_xml(channel)
                timestamp_xml = self._get_current_timestamp()
                context_and_task = f"""
<contexto_actual_y_tarea>
    {timestamp_xml}
    <usuario_actual>{user_name}</usuario_actual>
    {history_xml}
    <input_del_usuario>{user_input}</input_del_usuario>
</contexto_actual_y_tarea>
"""
                prompt_parts.append(context_and_task)
            # Adjuntar imágenes si existen
            if attachments:
                prompt_parts.append(
                    "\nEl usuario también ha adjuntado la(s) siguiente(s) imagen(es):"
                )
                for attachment in attachments:
                    image_bytes = await attachment.read()
                    img = Image.open(BytesIO(image_bytes))
                    prompt_parts.append(img)
        logger.info(
            f"Enviando prompt a Gemini. Tarea para: {user_name}. Input: '{user_input[:50]}...'"
        )
        response = await self.model.generate_content_async(prompt_parts)
        return response.text

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        # --- Lógica de Interacción ---
        # 1. Mención directa o respuesta al bot (siempre responde)
        is_mention = self.bot.user in message.mentions
        is_reply = (
            message.reference
            and message.reference.resolved
            and message.reference.resolved.author == self.bot.user
        )

        # 2. Saludo aleatorio (probabilidad baja)
        is_greeting = any(
            saludo in message.content.lower().split() for saludo in SALUDOS_COMUNES
        )
        should_greet = (
            is_greeting and random.random() < 0.15
        )  # 15% de probabilidad de responder a un saludo

        if not (is_mention or is_reply or should_greet):
            return

        # Verificar canal principal y personalidad cargada
        if not self.personality_prompt:
            return
        try:
            config = await self.bot.db_manager.get_guild_config(message.guild.id)
            if not config or message.channel.id != config.get("main_channel_id"):
                return
        except Exception as e:
            logger.error(
                f"Error al obtener config del guild en on_message: {e}",
                extra={"guild_id": message.guild.id},
            )
            return

        async with message.channel.typing():
            try:
                user_input = message.content
                if is_greeting and not (is_mention or is_reply):
                    user_input += "\n(Acabas de ver a este usuario saludar en el canal y decidiste responder por iniciativa propia)."

                response_text = await self._generate_gemini_response(
                    message.channel,
                    message.author.display_name,
                    user_input,
                    message.attachments,
                )
                if response_text:
                    await message.reply(response_text)
            except Exception as e:
                logger.error(
                    f"Error en on_message con Gemini: {e}",
                    exc_info=True,
                    extra={"guild_id": message.guild.id},
                )
                await message.reply(
                    "Ai... mi conexión con el saber arcano parece fallar. 💀"
                )

    @tasks.loop(minutes=20)  # Se ejecuta cada 20 minutos
    async def proactive_conversation_task(self):
        """
        Tarea que se ejecuta periódicamente para que Diami se una a una conversación
        de forma proactiva si el canal principal está activo.
        """
        # Probabilidad de iniciar la interacción para no ser demasiado intrusiva
        if random.random() > 0.20:  # 70% de las veces no hace nada
            return

        logger.info("Tarea proactiva iniciada, buscando un servidor activo...")
        # Iterar sobre todos los servidores donde está el bot
        for guild in self.bot.guilds:
            try:
                config = await self.bot.db_manager.get_guild_config(guild.id)
                if not config or not config.get("main_channel_id"):
                    continue

                channel_id = config.get("main_channel_id")
                channel = guild.get_channel(channel_id)

                if not channel or not isinstance(channel, discord.TextChannel):
                    continue

                # Verificar si ha habido actividad reciente en el canal
                last_message = await channel.fetch_message(channel.last_message_id)
                if (
                    last_message
                    and (
                        datetime.utcnow().replace(tzinfo=None)
                        - last_message.created_at.replace(tzinfo=None)
                    ).total_seconds()
                    < 600
                ):  # 10 minutos

                    logger.info(
                        f"Canal activo encontrado en '{guild.name}'. Diami se unirá a la conversación."
                    )

                    async with channel.typing():
                        # Le damos a la IA el contexto y una orden específica
                        user_input = "(Has estado observando la conversación en silencio y decides unirte. Lee el historial y haz un comentario relevante, una pregunta o una broma para integrarte a la charla. No saludes, simplemente continúa la conversación existente)."

                        response_text = await self._generate_gemini_response(
                            channel, "Diami", user_input
                        )
                        if response_text:
                            await channel.send(response_text)

                        # Solo actúa en un servidor por ciclo para no spammear
                        return

            except Exception as e:
                logger.error(
                    f"Error en la tarea proactiva para el servidor {guild.name}: {e}"
                )

    @proactive_conversation_task.before_loop
    async def before_proactive_task(self):
        """Espera a que el bot esté completamente listo antes de iniciar la tarea."""
        await self.bot.wait_until_ready()

    async def interpretar_tarot(self, user: str, pregunta: str, cartas: list) -> str:
        """
        Genera una interpretación de las cartas del tarot para una pregunta dada.
        Utiliza el modelo Gemini para crear una respuesta personalizada.

        Args:
            user (str): Nombre del usuario que realiza la pregunta.
            pregunta (str): La pregunta realizada por el usuario.
            cartas (list): Lista de tuplas (nombre_carta, orientacion), por ejemplo:
                [("El Loco", "derecha"), ("La Muerte", "invertida"), ...]

        Returns:
            str: Interpretación generada por Diami.
        """
        # Construir el prompt para la IA
        cartas_descripcion = "\n".join(
            [
                f"- {nombre.replace('_', ' ').title()} ({orientacion})"
                for nombre, orientacion in cartas
            ]
        )
        prompt = (
            f">>command>>\n"
            f"Pregunta: {pregunta}\n"
            f"Cartas extraídas:\n{cartas_descripcion}\n"
            "Como experta tarotista, interpreta el significado de estas cartas en relación a la pregunta. "
            "Sé clara, concisa y empática. No repitas la pregunta ni los nombres de las cartas, solo interpreta el mensaje que transmiten juntas."
        )
        try:
            response = await self._generate_gemini_response(
                None,  # No se requiere canal para la interpretación
                user,  # Nombre de la IA
                prompt,
                [],  # Sin adjuntos
            )
            return (
                response
                if response
                else "No pude interpretar las cartas en este momento."
            )
        except Exception as e:
            logger.error(f"Error al interpretar tarot: {e}", exc_info=True)
            return "Ocurrió un error al interpretar las cartas."


# ==============================================================================
# FUNCIÓN DE CARGA DEL COG
# ==============================================================================
async def setup(bot: commands.Bot):
    await bot.add_cog(AI(bot))
