# cogs/general.py
# ==============================================================================
# Cog section "diversion"
# ==============================================================================
import os
import logging
import discord
from discord.ext import commands
from discord import app_commands
import random
from PIL import Image


logger = logging.getLogger(__name__)

# ==============================================================================
# DATOS CONSTANTES
# ==============================================================================

TAROT_FOLDER = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "assets",
    "images",
    "tarot",
)
ARCANOS = [
    "the_fool.jpg",
    "the_magician.jpg",
    "the_high_priestess.jpg",
    "the_empress.jpg",
    "the_emperor.jpg",
    "the_hierophant.jpg",
    "the_lovers.jpg",
    "the_chariot.jpg",
    "the_strength.jpg",
    "the_hermit.jpg",
    "the_wheel_of_fortune.jpg",
    "the_justice.jpg",
    "the_hanged_man.jpg",
    "the_death.jpg",
    "the_temperance.jpg",
    "the_devil.jpg",
    "the_tower.jpg",
    "the_star.jpg",
    "the_moon.jpg",
    "the_sun.jpg",
    "the_judgement.jpg",
    "the_world.jpg",
]

# ==============================================================================
# Comando de Tarot
# ==============================================================================


class Fun(commands.Cog, name="Diversion"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="tarot", description="🎴 Haz una pregunta y consulta las cartas del tarot."
    )
    @app_commands.describe(
        ask="Que le quieres preguntar a las cartas.",
    )
    async def tarot(
        self,
        interaction: discord.Interaction,
        ask: str,
    ):
        """
        Comando principal de tarot. Selecciona 3 cartas únicas, decide su orientación y genera una imagen.
        Envía una respuesta deferida para evitar que la interacción expire mientras procesa la IA.
        """
        # Deferir la respuesta para evitar timeout de Discord
        await interaction.response.defer()

        # Selección de 3 cartas únicas
        cartas = random.sample(ARCANOS, 3)
        orientaciones = [random.choice(["derecha", "invertida"]) for _ in cartas]

        # Cargar imágenes y aplicar orientación
        imagenes = []
        for carta, orientacion in zip(cartas, orientaciones):
            path = os.path.join(TAROT_FOLDER, carta)
            img = Image.open(path)
            if orientacion == "invertida":
                img = img.rotate(180)
            imagenes.append(img)

        # Crear imagen final con margen entre cartas
        margen = 20
        ancho_total = sum(img.width for img in imagenes) + margen * 2
        alto_max = max(img.height for img in imagenes)
        resultado = Image.new("RGBA", (ancho_total, alto_max), (255, 255, 255, 0))
        x = margen
        for img in imagenes:
            resultado.paste(
                img,
                (x, (alto_max - img.height) // 2),
                img if img.mode == "RGBA" else None,
            )
            x += img.width
        # Guardar imagen temporal
        temp_path = os.path.join(TAROT_FOLDER, "temp_tarot.png")
        resultado.save(temp_path)

        # Construir mensaje de resultado
        cartas_info = [
            f"{os.path.splitext(c)[0].replace('_', ' ').title()} ({o})"
            for c, o in zip(cartas, orientaciones)
        ]
        descripcion = f"Pregunta: {ask}\n\nCartas:\n" + "\n".join(cartas_info)

        # Obtener interpretación de Diami usando IA
        ai_cog = self.bot.get_cog("Inteligencia Artificial Diami")
        interpretacion = None
        if ai_cog:
            # Preparamos la lista de cartas para la IA (nombre, orientación)
            cartas_para_ia = [
                (os.path.splitext(c)[0].replace("_", " ").title(), o)
                for c, o in zip(cartas, orientaciones)
            ]
            try:
                interpretacion = await ai_cog.interpretar_tarot(
                    interaction.user.name, ask, cartas_para_ia
                )
            except Exception as e:
                logger.error(f"Error al obtener interpretación de tarot: {e}")
                interpretacion = "No se pudo obtener la interpretación de las cartas."
        else:
            interpretacion = "La IA no está disponible para interpretar las cartas."

        # Enviar imagen y resultados como respuesta usando followup
        # Adjuntar la imagen al embed correctamente usando 'url' y 'attachment://tarot.png'
        embed = discord.Embed(
            title="Lectura de Tarot",
            description=descripcion,
            color=discord.Color.purple(),
        )
        embed.add_field(
            name="Interpretación de Diami", value=interpretacion, inline=False
        )
        embed.set_footer(text="DiamiBot - Tarot IA")
        # Adjuntar la imagen al embed
        file = discord.File(temp_path, filename="tarot.png")
        embed.set_image(url="attachment://tarot.png")
        await interaction.followup.send(embed=embed, file=file)
        # Eliminar imagen temporal
        os.remove(temp_path)


# ==============================================================================
# FUNCIÓN DE CARGA DEL COG
# ==============================================================================
async def setup(bot: commands.Bot):
    await bot.add_cog(Fun(bot))
