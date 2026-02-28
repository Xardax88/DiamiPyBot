# app/cogs/general.py
import logging
import os
import random

import discord
from discord import TextStyle, app_commands, ui
from discord.ext import commands

from dashboard.dash import footer

logger = logging.getLogger(__name__)

# ==============================================================================
# DATOS CONSTANTES
# ==============================================================================
CONFESSION_ICON = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "assets",
    "images",
    "icons",
    "user.png",
)

HERESY_ICON = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "assets",
    "images",
    "icons",
    "heresy.png",
)


HERESY_TEXTS = [
    "He detectado herejía. El Emperador Desaprueba.",
    "Esto suena a pensamiento herético. El Ordo Hereticus ha sido notificado.",
    "Suficiente. Por el Trono Dorado, purgaré esta abominación.",
    "Huele a disformidad por aquí... y no me gusta.",
    "Tu falta de fe, resulta molesta...",
    "El Emperador no tolera la herejía. ¡Purgaré esta abominación!",
    "¡El Emperador Protege! Y yo también, de la herejía.",
    "El Codex Astartes no aprueba esta conducta.",
]


# ==============================================================================
# MODALES (Pop-ups de Interacción)
# ==============================================================================
class ConfessionModal(ui.Modal, title="📝 Confesión Anónima"):
    confession_text = ui.TextInput(
        label="Escribe tu confesión aquí",
        style=TextStyle.long,
        placeholder="Nadie sabrá que fuiste tú...",
        required=True,
        max_length=2000,
    )

    def __init__(self, bot: commands.Bot, guild_id: int):
        super().__init__()
        self.bot = bot
        self.guild_id = guild_id

    async def on_submit(self, interaction: discord.Interaction):
        config = await self.bot.db_manager.get_guild_config(self.guild_id)
        if not (config and (channel_id := config.get("confession_channel_id"))):
            await interaction.response.send_message(
                "Lo siento, el canal de confesiones no ha sido configurado.",
                ephemeral=True,
            )
            return

        confession_channel = self.bot.get_channel(channel_id)
        if not confession_channel:
            await interaction.response.send_message(
                "No puedo encontrar el canal de confesiones. Puede que haya sido eliminado.",
                ephemeral=True,
            )
            return

        try:
            thumbnail_file = discord.File(CONFESSION_ICON, filename="thumbnail.png")
            embed = discord.Embed(
                title="Confesión Anónima",
                description=f"{self.confession_text.value}",
                color=discord.Color.dark_grey(),
                # timestamp=discord.utils.utcnow(),
            )
            embed.set_thumbnail(url="attachment://thumbnail.png")
            embed.set_footer(
                text=f"\u200b\t\u200b\t\u200b\t\u200b\t\u200b\t\u200b\t\u200b\t\u200b\t"
                f"\u200b\t\u200b\t\u200b\t\u200b\t\u200b\t\u200b\t\u200b\t\u200b\t"
                f"\u200b\t\u200b\t\u200b\t\u200b\t\u200b\t\u200b\t\u200b\t\u200b\t"
            )

            await confession_channel.send(embed=embed, file=thumbnail_file)
            await interaction.response.send_message(
                "Tu confesión ha sido enviada de forma anónima.", ephemeral=True
            )
        except discord.Forbidden:
            logger.warning(
                f"No se pudo enviar confesión en {self.guild_id} por falta de permisos.",
                extra={"guild_id": interaction.guild.id},
            )
            await interaction.response.send_message(
                "No tengo permisos para enviar mensajes en el canal de confesiones.",
                ephemeral=True,
            )
        except Exception as e:
            logger.error(
                f"Error al procesar confesión: {e}",
                exc_info=True,
                extra={"guild_id": interaction.guild.id},
            )
            await interaction.response.send_message(
                f"Ocurrió un error al procesar tu confesión: {e}",
                ephemeral=True,
            )


# ==============================================================================
# COG PRINCIPAL (General)
# ==============================================================================
class General(commands.Cog, name="General"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # --- REGISTRO DE MENÚ CONTEXTUAL ---
        self.heresy_context_menu = app_commands.ContextMenu(
            name="Declarar Herejía",
            callback=self.heresy_context_menu_callback,
        )
        self.bot.tree.add_command(self.heresy_context_menu)

    def cog_unload(self):
        # Limpieza al descargar el cog
        self.bot.tree.remove_command(
            self.heresy_context_menu.name, type=self.heresy_context_menu.type
        )

    # --- FUNCIÓN HELPER PARA ENVIAR EL EMBED DE HEREJÍA ---
    # La movemos aquí para que sea accesible por el comando slash y el menú contextual.
    async def _send_heresy_embed(
        self,
        interaction: discord.Interaction,
        target: discord.Member,
        reply_to_message: discord.Message = None,
    ):
        try:
            heresy_folder_path = "assets/images/heresy"
            available_images = [
                f
                for f in os.listdir(heresy_folder_path)
                if os.path.isfile(os.path.join(heresy_folder_path, f))
            ]
            if not available_images:
                await interaction.response.send_message(
                    "Mi armería está vacía.", ephemeral=True
                )
                return

            random_image_name = random.choice(available_images)
            files = [
                discord.File(
                    os.path.join(heresy_folder_path, random_image_name),
                    filename=random_image_name,
                ),
                discord.File(HERESY_ICON, filename="thumbnail.png"),
            ]

            embed = discord.Embed(
                title="HEREJÍA!",
                description=random.choice(HERESY_TEXTS),
                color=discord.Color.red(),
            )
            embed.add_field(
                name=f"Evidencia presentada por ",
                value=f"**{interaction.user.mention}**.",
                inline=False,
            )
            embed.add_field(
                name=f"Se declara hereje a ",
                value=f"**{target.mention}**.",
                inline=False,
            )
            embed.set_footer(text="El Emperador Protege.")
            embed.set_image(url=f"attachment://{random_image_name}")
            embed.set_thumbnail(url="attachment://thumbnail.png")

            if reply_to_message:
                # Si se proporciona un mensaje (desde el menú contextual), hacemos reply.
                await reply_to_message.reply(embed=embed, files=files)

                # Y enviamos una confirmación silenciosa y efímera a la interacción
                # para que Discord sepa que hemos respondido.
                if not interaction.response.is_done():
                    await interaction.response.send_message(
                        "¡Herejía purgada!", ephemeral=True, delete_after=1
                    )
            else:
                # Si no hay mensaje para responder (desde el comando slash),
                # enviamos la respuesta directamente a la interacción.
                if not interaction.response.is_done():
                    await interaction.response.send_message(embed=embed, files=files)
                else:
                    # Este caso es poco probable con un comando simple, pero es una buena práctica.
                    await interaction.followup.send(embed=embed, files=files)

        except Exception as e:
            logger.error(
                f"Error en comando de herejía: {e}",
                exc_info=True,
                extra={"guild_id": interaction.guild.id},
            )
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "El juicio del Emperador ha sido interrumpido.", ephemeral=True
                )

    # --- COMANDO DE HEREJÍA ---
    @app_commands.command(
        name="herejia", description="☠️ Declara hereje a un miembro del servidor."
    )
    @app_commands.describe(usuario="El miembro al que quieres declarar hereje.")
    async def heresy(self, interaction: discord.Interaction, usuario: discord.Member):
        """Declara hereje a un usuario específico."""
        # Llamamos al helper sin un mensaje para responder.
        await self._send_heresy_embed(interaction, target=usuario)

    # --- COMANDO DE CONFESIÓN ANÓNIMA ---
    @app_commands.command(
        name="confesion", description="🤫 Envía una confesión anónima."
    )
    async def confess(self, interaction: discord.Interaction):
        """Abre el modal para que el usuario escriba su confesión."""
        if not interaction.guild_id:
            await interaction.response.send_message(
                "Este comando solo puede usarse en un servidor.", ephemeral=True
            )
            return

        modal = ConfessionModal(self.bot, interaction.guild_id)
        await interaction.response.send_modal(modal)

    # --- CALLBACKS DE MENÚS CONTEXTUALES ---

    async def heresy_context_menu_callback(
        self, interaction: discord.Interaction, message: discord.Message
    ):
        """Callback para el menú contextual de herejía."""
        # Llamamos al helper pasando el mensaje original para que pueda hacer reply.
        await self._send_heresy_embed(
            interaction, target=message.author, reply_to_message=message
        )


# ==============================================================================
# FUNCIÓN DE CARGA DEL COG
# ==============================================================================
async def setup(bot: commands.Bot):
    await bot.add_cog(General(bot))
