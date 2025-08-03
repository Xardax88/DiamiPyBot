import logging
import discord
from discord.ext import commands
import os
import random

logger = logging.getLogger("discord")


# ==============================================================================
# Cog para Eventos de Miembros
# ==============================================================================
class MemberEvents(commands.Cog, name="member_events"):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ==============================================================================
    # Evento que se ejecuta cuando un usuario se une al servidor
    # ==============================================================================
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """
        Evento que se ejecuta cuando un usuario se une al servidor.
        Utiliza la IA Diami para generar un mensaje de bienvenida personalizado,
        recordando al usuario revisar el canal de reglas y adjuntando una imagen
        aleatoria de bienvenida desde la carpeta assets/images/welcome.
        """
        config = await self.bot.db_manager.get_guild_config(member.guild.id)
        if not config or not config.get("features", {}).get(
            "welcome_message_enabled", False
        ):
            return
        if not config or not config.get("main_channel_id"):
            return

        channel = self.bot.get_channel(config["main_channel_id"])
        rules_channel = self.bot.get_channel(config.get("rules_channel_id"))

        # Selección aleatoria de imagen de bienvenida
        welcome_images_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "assets",
            "images",
            "welcome",
        )
        welcome_images = [
            f
            for f in os.listdir(welcome_images_path)
            if os.path.isfile(os.path.join(welcome_images_path, f))
        ]
        image_file = None
        if welcome_images:
            image_file = os.path.join(
                welcome_images_path, random.choice(welcome_images)
            )

        # Obtiene el cog de la IA Diami
        ai_cog = self.bot.get_cog("Inteligencia Artificial Diami")
        reglas_mention = rules_channel.mention if rules_channel else "(canal de reglas)"
        prompt = (
            f">>command>>"
            f"Un nuevo usuario llamado {member.mention} acaba de unirse al servidor. "
            f"Dale la bienvenida y recuérdale amablemente que lea las reglas en {reglas_mention}. "
            f"Hazlo de forma cálida y amigable."
        )
        if ai_cog:
            # Genera el mensaje usando Diami
            mensaje = await ai_cog._generate_gemini_response(
                channel=channel, user_name="Diami", user_input=prompt, attachments=[]
            )
            # Envía el mensaje y la imagen si existe
            if image_file:
                with open(image_file, "rb") as img:
                    file = discord.File(img, filename=os.path.basename(image_file))
                    await channel.send(content=mensaje, file=file)
            else:
                await channel.send(content=mensaje)
        else:
            # Fallback si la IA no está disponible
            fallback_msg = f"¡Bienvenido {member.mention} a {member.guild.name}! 🎉 Por favor revisa el canal de reglas: {rules_channel.mention if rules_channel else ''}"
            if image_file:
                with open(image_file, "rb") as img:
                    file = discord.File(img, filename=os.path.basename(image_file))
                    await channel.send(content=fallback_msg, file=file)
            else:
                await channel.send(content=fallback_msg)


# ==============================================================================
# FUNCIÓN DE CARGA DEL COG
# ==============================================================================
async def setup(bot: commands.Bot):
    """Función para cargar el cog en el bot."""
    await bot.add_cog(MemberEvents(bot))
