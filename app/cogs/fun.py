# cogs/general.py
# ==============================================================================
# Cog section "diversion"
# ==============================================================================
import os
from io import BytesIO
import logging
import discord
from discord.ext import commands
from discord import app_commands
import random
from PIL import Image
import imageio


logger = logging.getLogger(__name__)

# ==============================================================================
# DATOS CONSTANTES
# ==============================================================================

ROLL_ICON = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "assets",
    "images",
    "icons",
    "dice.png",
)

TAROT_ICON = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "assets",
    "images",
    "icons",
    "tarot.png",
)

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
# Comando Fun
# ==============================================================================


class Fun(commands.Cog, name="Diversion"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ==============================================================================
    # Comando de Tarot
    # ==============================================================================

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
        # temp_path = os.path.join(
        #     TAROT_FOLDER, f"temp_tarot_{interaction.user.name}.png"
        # )
        # resultado.save(temp_path)
        buffer = BytesIO()
        resultado.save(buffer, format="PNG")
        buffer.seek(0)

        files = [
            discord.File(fp=buffer, filename="tarot.png"),
            discord.File(TAROT_ICON, filename="thumbnail.png"),
        ]

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
            # Formatear la lista de cartas seleccionadas como string legible
            cartas_str = ", ".join(
                [f"{nombre}({orientacion})" for nombre, orientacion in cartas_para_ia]
            )
            # Loguear el formato solicitado para mayor claridad
            logger.info(
                f"Cartas seleccionadas: {cartas_str}",
                extra={"guild_id": interaction.guild.id},
            )
            try:
                interpretacion = await ai_cog.interpretar_tarot(
                    interaction.user.name, ask, cartas_para_ia
                )
            except Exception as e:
                logger.error(
                    f"Error al obtener interpretación de tarot: {e}",
                    extra={"guild_id": interaction.guild.id},
                )
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
        embed.set_thumbnail(url="attachment://thumbnail.png")
        embed.add_field(
            name="Interpretación de Diami", value=interpretacion, inline=False
        )
        embed.set_footer(text="DiamiBot - Tarot IA")
        # Adjuntar la imagen al embed
        # file = discord.File(temp_path, filename="tarot.png")
        embed.set_image(url="attachment://tarot.png")
        await interaction.followup.send(embed=embed, files=files)
        # Eliminar imagen temporal
        # os.remove(temp_path)

    # ==============================================================================
    # Comando de lanzamiento de dados
    # ==============================================================================
    @app_commands.command(
        name="roll",
        description="🎲 Lanza dados con notación D&D (ej: 2D6+3) y muestra el resultado.",
    )
    @app_commands.describe(tirada="Expresión de la tirada (ejemplo: 1D20+2, 2D6-1, D8)")
    async def dado(self, interaction: discord.Interaction, tirada: str):
        """
        Comando para lanzar dados usando la notación estándar de D&D.
        Permite expresiones como 1D20+2, 2D6-1, D8, etc.
        """
        await interaction.response.defer(thinking=True)

        try:
            # Parseo de la expresión de tirada
            import re

            patron = r"^(?:(\d*)[dD](\d+))([+-]?\d+)?$"
            match = re.match(patron, tirada.replace(" ", ""))

            if not match:
                await interaction.followup.send(
                    "❌ Formato inválido. Usa el formato XdY+Z, por ejemplo: 2D6+1, D20, 1d8-2."
                )
                return

            cantidad = int(match.group(1)) if match.group(1) else 1
            caras = int(match.group(2))
            modificador = int(match.group(3)) if match.group(3) else 0
            if cantidad < 1 or cantidad > 100 or caras < 2 or caras > 1000:
                await interaction.followup.send(
                    "❌ Cantidad de dados (1-100) o caras (2-1000) fuera de rango permitido."
                )
                return

            # Lanzar los dados
            resultados = [random.randint(1, caras) for _ in range(cantidad)]
            suma = sum(resultados) + modificador

            # Construir mensaje de resultado
            detalle = f"{' + '.join(map(str, resultados))}"
            if modificador:
                detalle += f" {'+' if modificador > 0 else '-'} {abs(modificador)}"
            embed = discord.Embed(
                title="Resultado de la tirada",
                description=f"Expresión: `{tirada}`",
                color=discord.Color.green(),
            )
            embed.add_field(
                name="Detalle",
                value=f"Dados: {detalle}\nTotal: **{suma}**",
                inline=False,
            )
            embed.set_footer(text="Lanzador de dados D&D")
            thumbnail_file = discord.File(ROLL_ICON, filename="thumbnail.png")
            embed.set_thumbnail(url="attachment://thumbnail.png")

            await interaction.followup.send(embed=embed, file=thumbnail_file)
        except Exception as e:
            logger.error(
                f"Error en el comando dado: {e}",
                extra={"guild_id": interaction.guild.id},
            )
            await interaction.followup.send(
                "❌ Ocurrió un error al procesar la tirada."
            )

    # ==============================================================================
    # Comando de meme "triggered"
    # ==============================================================================
    @app_commands.command(
        name="triggerd", description="🤬 Genera un meme 'triggered' con tu avatar."
    )
    async def triggerd(self, interaction: discord.Interaction):
        """
        Comando que toma el avatar del usuario, le aplica un efecto de temblor y le agrega el GIF 'triggered' en la parte inferior.
        """
        await interaction.response.defer()
        try:
            # Obtener el avatar del usuario
            avatar_url = interaction.user.display_avatar.replace(
                format="png", size=256
            ).url
            async with interaction.client.http._HTTPClient__session.get(
                avatar_url
            ) as resp:
                avatar_bytes = await resp.read()
            avatar_img = Image.open(BytesIO(avatar_bytes)).convert("RGBA")

            # Cargar el GIF 'triggered'
            triggered_gif_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "assets",
                "images",
                "triggered",
                "triggered.gif",
            )
            triggered_gif = imageio.mimread(triggered_gif_path)
            triggered_gif_height = triggered_gif[0].shape[0]
            triggered_gif_width = triggered_gif[0].shape[1]

            # Redimensionar el avatar un poco más grande que el ancho del GIF 'triggered' para evitar bordes negros al sacudir
            AVATAR_OVERSIZE = 1.25  # Factor de escala para el avatar
            avatar_size = int(triggered_gif_width * AVATAR_OVERSIZE)
            avatar_img = avatar_img.resize((avatar_size, avatar_size))

            frames = []
            # Generar frames con efecto de temblor
            for i, triggered_frame in enumerate(triggered_gif):
                # Efecto de temblor: desplazar aleatoriamente el avatar
                dx = random.randint(
                    -int((avatar_size - triggered_gif_width) / 2),
                    int((avatar_size - triggered_gif_width) / 2),
                )
                dy = random.randint(
                    -int((avatar_size - triggered_gif_width) / 2),
                    int((avatar_size - triggered_gif_width) / 2),
                )
                base = Image.new(
                    "RGBA",
                    (triggered_gif_width, triggered_gif_height + triggered_gif_width),
                    (0, 0, 0, 0),
                )
                # Pegar el avatar centrado y desplazado
                base.paste(
                    avatar_img,
                    (
                        dx - int((avatar_size - triggered_gif_width) / 2),
                        dy - int((avatar_size - triggered_gif_width) / 2),
                    ),
                )
                # Superponer el frame del GIF 'triggered' en la parte inferior
                triggered_pil = Image.fromarray(triggered_frame)
                if triggered_pil.mode != "RGBA":
                    triggered_pil = triggered_pil.convert("RGBA")
                # Usar el canal alfa como máscara de transparencia
                base.paste(
                    triggered_pil, (0, triggered_gif_width), triggered_pil.split()[3]
                )
                frames.append(base)

            # Guardar el resultado en un buffer
            buffer = BytesIO()
            frames[0].save(
                buffer,
                format="GIF",
                save_all=True,
                append_images=frames[1:],
                duration=40,
                loop=0,
                disposal=2,
                transparency=0,
            )
            buffer.seek(0)

            file = discord.File(buffer, filename="triggered.gif")
            await interaction.followup.send(
                file=file, content=f"{interaction.user.mention} se TRIGGERIO!"
            )
        except Exception as e:
            logger.error(
                f"Error en el comando triggerd: {e}",
                extra={"guild_id": interaction.guild.id},
            )
            await interaction.followup.send(
                "❌ Ocurrió un error al generar el meme triggered."
            )


# ==============================================================================
# FUNCIÓN DE CARGA DEL COG
# ==============================================================================
async def setup(bot: commands.Bot):
    await bot.add_cog(Fun(bot))
