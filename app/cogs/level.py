import discord
from discord.ext import commands
import logging
from ..core.database import DatabaseManager
from ..core.canvas import CanvasRank
import io
import time

logger = logging.getLogger(__name__)


class Level(commands.Cog):
    """
    Cog para gestionar el sistema de experiencia y niveles de los usuarios.
    Los usuarios ganan experiencia por enviar mensajes. La experiencia se almacena en la base de datos.
    """

    def __init__(self, bot: commands.Bot, db_manager: DatabaseManager):
        self.bot = bot
        self.db_manager = db_manager
        # Diccionario para almacenar el último timestamp de XP por usuario y servidor
        self.last_xp_time = {}  # {(guild_id, user_id): timestamp}
        self.last_msg = {}  # {(guild_id, user_id): last_message_content}

    # --- Add XP por mensaje ---
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """
        Evento que se ejecuta cada vez que se recibe un mensaje.
        Otorga experiencia al autor del mensaje si no es un bot y el mensaje es en un servidor.
        Se aplica un temporizador para evitar otorgar XP en intervalos muy cortos.
        """
        # Ignorar mensajes de bots o fuera de servidores
        if message.author.bot or not message.guild:
            return

        user_id = message.author.id
        guild_id = message.guild.id

        # Ignorar mensajes demasiado cortos
        if len(message.content) < 10:
            return

        # Ignora mensajes que contengan urls
        if any(word.startswith("http") for word in message.content.split()):
            return

        # Ignora mensajes que contengan menos del 40% de letras
        letters = "".join(filter(str.isalpha, message.content))
        parsent = len(letters) / len(message.content)
        if parsent < 0.4:
            return

        # Ignorar mensaje repetido
        last_message = self.last_msg.get((guild_id, user_id), "")
        if last_message == message.content:
            return
        self.last_msg[(guild_id, user_id)] = message.content

        # Verifica que pase tiempo desde el último XP otorgado
        cooldown = 10  # Tiempo en segundos entre otorgamientos de XP
        now = time.time()
        key = (guild_id, user_id)
        last_time = self.last_xp_time.get(key, 0)
        if now - last_time < cooldown:
            return
        self.last_xp_time[key] = now

        # XP otorgada por mensaje
        xp_to_add = 10
        await self.db_manager.add_xp(guild_id, user_id, xp_to_add)
        logger.info(
            f"Usuario {user_id} ha recibido {xp_to_add} XP en el guild {guild_id}.",
            extra={"guild_id": guild_id},
        )

    # --- Comando Slash para mostrar nivel y experiencia ---
    @discord.app_commands.command(
        name="rank",
        description="🔝 Muestra tu experiencia y nivel actual o el de otro usuario.",
    )
    @discord.app_commands.describe(
        usuario="Usuario del que quieres ver el rank (opcional)"
    )
    async def rank(
        self, interaction: discord.Interaction, usuario: discord.User = None
    ):
        """
        Comando slash que muestra la experiencia y el nivel del usuario que lo ejecuta o de otro usuario, junto a una imagen personalizada.
        Si se proporciona un usuario, muestra el rank de ese usuario.
        """
        # Determinar el usuario objetivo
        target_user = usuario or interaction.user
        user_id = target_user.id
        user_avatar = (
            target_user.avatar.url
            if target_user.avatar
            else target_user.default_avatar.url
        )
        user_name = (
            target_user.display_name
            if hasattr(target_user, "display_name")
            else target_user.name
        )

        # Verificar si el usuario es un bot y asignar rol correspondiente
        user_rol = "User"
        if target_user.bot:
            user_rol = "Bot"
        elif (
            hasattr(target_user, "guild_permissions")
            and target_user.guild_permissions.administrator
        ):
            user_rol = "Admin"
        elif (
            hasattr(target_user, "guild_permissions")
            and target_user.guild_permissions.manage_messages
        ):
            user_rol = "Mod"

        guild_id = interaction.guild.id if interaction.guild else None
        if not guild_id:
            await interaction.response.send_message(
                "Este comando solo puede usarse en servidores.", ephemeral=True
            )
            return
        # Obtener experiencia del usuario desde la base de datos
        user_level = await self.db_manager.get_user_level(guild_id, user_id)

        # Si el usuario no tiene datos en la base, asignar xp = 0
        if user_level and "xp" in user_level and user_level["xp"] is not None:
            xp = user_level["xp"]
        else:
            xp = 0

        if user_rol == "Bot":
            # xp = 1000000000
            xp = 1724004175

        # Calcular nivel usando la función lvl_cal
        lvl, exp_base, next_level_exp = self.lvl_cal(xp)
        # Generar imagen de rank
        canvas = CanvasRank(
            guild_id=guild_id,
            user_id=user_id,
            user_name=user_name,
            role=user_rol,
            avatar_url=user_avatar,
            level=lvl,
            exp=xp,
            next_level_exp=next_level_exp,
            previous_level_exp=exp_base,
        )
        image = canvas.render()
        # Convertir imagen a bytes para enviar a Discord
        with io.BytesIO() as image_binary:
            image.save(image_binary, format="PNG")
            image_binary.seek(0)
            file = discord.File(fp=image_binary, filename="rank.png")
            await interaction.response.send_message(
                file=file,
            )

    # --- Método estático para calcular el nivel ---
    @staticmethod
    def lvl_cal(exp: int, base: int = 200, factor: float = 1.2) -> tuple[int, int, int]:
        """
        Calcula el nivel de un personaje en base a su experiencia.

        Parámetros:
        - exp (int): Experiencia total acumulada por el personaje.
        - base (int): Experiencia base requerida para subir de nivel desde el nivel 1.
        - factor (float): Multiplicador que determina cuánto crece la experiencia requerida por nivel.

        Retorna:
        - tuple: (nivel alcanzado, experiencia base del nivel actual, experiencia requerida para el siguiente nivel)
        """
        lvl = 1
        next_level_exp = base
        exp_base = 0
        exp_total = exp

        while exp >= next_level_exp:
            exp -= next_level_exp
            exp_base += next_level_exp
            lvl += 1
            next_level_exp = int(next_level_exp * factor)

        # exp_base_actual es la experiencia total acumulada hasta el inicio del nivel actual
        # next_level_exp es la experiencia necesaria para el siguiente nivel
        return lvl, exp_base, next_level_exp


async def setup(bot: commands.Bot):
    """
    Función necesaria para cargar el cog en el bot. Se obtiene la instancia de db_manager desde el bot.
    """
    db_manager = getattr(bot, "db_manager", None)
    if db_manager is None:
        raise RuntimeError("No se encontró la instancia de DatabaseManager en el bot.")
    await bot.add_cog(Level(bot, db_manager))
