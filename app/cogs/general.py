# cogs/general.py
import os
import logging
import discord
from discord.ext import commands
from discord import app_commands
import random

logger = logging.getLogger(__name__)

HERESY_TEXTS = [
    "He detectado herejía. El Emperador Desaprueba.",
    "Esto suena a pensamiento herético. El Ordo Hereticus ha sido notificado.",
    "Suficiente. Por el Trono Dorado, purgaré esta abominación.",
    "Huele a disformidad por aquí... y no me gusta.",
    "Tu falta de fe, resulta molesta...",
    "¡HEREJÍA! *BLAM!*"
]


class General(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.heresy_context_menu = app_commands.ContextMenu(
            name='Declarar Herejía',
            callback=self.heresy_context_menu_callback,
        )
        self.bot.tree.add_command(self.heresy_context_menu)

    async def cog_unload(self):
        self.bot.tree.remove_command(self.heresy_context_menu.name, type=self.heresy_context_menu.type)

    async def _send_heresy_embed(self, interaction: discord.Interaction, target_message: discord.Message = None):
        heresy_folder_path = "assets/images/heresy"
        thumbnail_path = "assets/images/Heresy.png"

        try:
            available_images = [f for f in os.listdir(heresy_folder_path) if
                                os.path.isfile(os.path.join(heresy_folder_path, f))]

            if not available_images:
                await interaction.response.send_message("Quiero purgar, pero mi armería está vacía.", ephemeral=True)
                return

            random_image_name = random.choice(available_images)
            image_path = os.path.join(heresy_folder_path, random_image_name)

            image_file = discord.File(image_path, filename=random_image_name)
            thumbnail_file = discord.File(thumbnail_path, filename="thumbnail.png")
            files_to_send = [image_file, thumbnail_file]

            embed = discord.Embed(
                title="HEREJÍA!",
                color=discord.Color.red()
            )

            # --- La lógica de construcción del embed no cambia ---
            if target_message:
                quote = f"La evidencia presentada por {target_message.author.mention}."
                embed.description = quote
                embed.add_field(name="Sentencia del Inquisidor", value=random.choice(HERESY_TEXTS), inline=False)
            else:
                embed.description = random.choice(HERESY_TEXTS)

            embed.set_footer(text="El Emperador Protege.")
            embed.set_image(url=f"attachment://{random_image_name}")
            embed.set_thumbnail(url="attachment://thumbnail.png")

            # --- LÓGICA DE ENVÍO MODIFICADA ---
            if target_message:
                # Si hay un mensaje objetivo (menú contextual), respondemos a ESE mensaje.
                await target_message.reply(embed=embed, files=files_to_send)
                # Y luego enviamos una confirmación efímera a la interacción para que no falle.
                if not interaction.response.is_done():
                    await interaction.response.send_message("¡Herejía purgada!", ephemeral=True)
            else:
                # Si no hay mensaje objetivo (comando slash), respondemos a la interacción como antes.
                await interaction.response.send_message(embed=embed, files=files_to_send)

        except discord.errors.Forbidden:
            # Error común si el bot no tiene permisos para enviar mensajes o archivos en el canal.
            logger.warning(f"No se pudo responder en el canal {interaction.channel.name} por falta de permisos.")
            if not interaction.response.is_done():
                await interaction.response.send_message("No tengo permisos para purgar en este canal.", ephemeral=True)
        except FileNotFoundError as e:
            logger.error(f"No se encontró un archivo para el comando de herejía: {e.filename}")
            user_error = "No encuentro mi sello inquisitorial... (falta el logo)." if str(
                e.filename) == thumbnail_path else "No encuentro mi santuario de purga... (falta la carpeta)."
            if not interaction.response.is_done():
                await interaction.response.send_message(user_error, ephemeral=True)
        except Exception as e:
            logger.error(f"Error inesperado en la función de herejía: {e}", exc_info=True)
            user_error = "Algo ha interferido con el juicio del Emperador. Inténtalo de nuevo."
            if not interaction.response.is_done():
                await interaction.response.send_message(user_error, ephemeral=True)

    # --- Comandos /ping y /herejia sin cambios ---
    @app_commands.command(name="ping", description="📈 Muestra la latencia del bot con el servidor de Discord.")
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        embed = discord.Embed(title="🏓 Pong!", description=f"La latencia actual es de **{latency}ms**.",
                              color=discord.Color.green() if latency < 150 else discord.Color.orange())
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="herejia", description="☠️ Declara una herejía de forma general.")
    async def heresy_slash(self, interaction: discord.Interaction):
        await self._send_heresy_embed(interaction)

    # --- El callback del menú contextual ahora no necesita 'defer' ---
    async def heresy_context_menu_callback(self, interaction: discord.Interaction, message: discord.Message):
        """
        Este es el callback que se ejecuta cuando se usa el menú contextual.
        Llama a la función de herejía pasándole el mensaje objetivo.
        """
        # Ya no necesitamos defer(), la respuesta a la interacción será casi instantánea.
        await self._send_heresy_embed(interaction, target_message=message)


async def setup(bot: commands.Bot):
    await bot.add_cog(General(bot))