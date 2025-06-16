# app/cogs/help.py
import math
from typing import Optional, List
import discord
from discord import app_commands
from discord.ext import commands

# --- CONFIGURACIÓN ---
HIDDEN_COGS = ['Help', 'ScheduledTasks', 'LoggingEvents']
COMMANDS_PER_PAGE = 5
HOME_VALUE = "_GO_HOME_"  # Valor especial para la opción de volver al inicio


# ==============================================================================
# COMPONENTE REUTILIZABLE: MENÚ DE SELECCIÓN DE CATEGORÍAS
# ==============================================================================
class CategorySelect(discord.ui.Select):
    """
    Un menú de selección que se puede usar en múltiples vistas.
    Muestra las categorías y permite volver al menú principal.
    """
    def __init__(self, categories: List[str], current_category: Optional[str] = None):
        placeholder = current_category if current_category else "Categorías"

        options = [
            discord.SelectOption(
                label="Categorías",
                value=HOME_VALUE,
                description="Vista principal de categorías."
            )
        ]

        for category in sorted(categories):
            options.append(
                discord.SelectOption(
                    label=category,
                    description=f"Ver comandos de {category}",
                    default=(category == current_category)  # Marca la categoría actual como seleccionada
                )
            )

        super().__init__(placeholder=placeholder, options=options, row=1)

    async def callback(self, interaction: discord.Interaction):
        selected_value = self.values[0]

        if selected_value == HOME_VALUE:
            parent_view = self.view.parent_view if hasattr(self.view, 'parent_view') else self.view
            await interaction.response.edit_message(embed=parent_view.initial_embed, view=parent_view)
            return

        parent_view = self.view.parent_view if hasattr(self.view, 'parent_view') else self.view
        pagination_view = PaginationView(interaction.client, interaction, selected_value, parent_view)
        initial_page_embed = pagination_view._generate_page_embed()
        await interaction.response.edit_message(embed=initial_page_embed, view=pagination_view)


# ==============================================================================
# VISTA DE PAGINACIÓN DE COMANDOS
# ==============================================================================
class PaginationView(discord.ui.View):
    def __init__(self, bot: commands.Bot, interaction: discord.Interaction, cog_name: str, parent_view: 'HelpView'):
        super().__init__(timeout=180)
        self.bot = bot
        self.interaction = interaction
        self.cog_name = cog_name
        self.parent_view = parent_view  # La vista principal original
        self.commands = self._get_cog_commands()
        self.current_page = 0
        self.total_pages = math.ceil(len(self.commands) / COMMANDS_PER_PAGE) if self.commands else 1

        # Añadimos el menú de selección, pasando la categoría actual
        self.add_item(CategorySelect(self.parent_view.categories, self.cog_name))
        self._update_buttons()

    def _get_cog_commands(self) -> list:
        cog = self.bot.get_cog(self.cog_name)
        if not cog: return []

        all_commands = []

        def process_command(command, prefix=""):
            if isinstance(command, app_commands.Group):
                for sub_cmd in command.commands:
                    process_command(sub_cmd, prefix=f"{prefix}{command.name} ")
            else:
                setattr(command, 'full_name', f"{prefix}{command.name}")
                all_commands.append(command)

        for cmd in cog.get_app_commands():
            process_command(cmd)
        return all_commands

    def _update_buttons(self):
        self.previous_page_button.disabled = self.current_page == 0
        self.next_page_button.disabled = self.current_page >= self.total_pages - 1

    def _generate_page_embed(self) -> discord.Embed:
        embed = discord.Embed(
            title=f"Página {self.current_page + 1} de {self.total_pages}",
            color=0x2b2d31
        )
        embed.set_author(name=f"Comandos de {self.cog_name}", icon_url=self.bot.user.display_avatar.url)
        start_index = self.current_page * COMMANDS_PER_PAGE
        end_index = start_index + COMMANDS_PER_PAGE
        page_commands = self.commands[start_index:end_index]
        if not page_commands:
            description = f"» **Lista de comandos (0)**\n\nNo hay comandos en esta categoría."
        else:
            description = f"» **Lista de comandos ({len(self.commands)})**\n\n"
            for cmd in page_commands:
                description += f"`/{cmd.full_name}`\n╰ {cmd.description}\n\n"
        embed.description = description
        embed.set_footer(text="© Xardax")
        return embed

    async def update_view(self, interaction: discord.Interaction):
        self._update_buttons()
        embed = self._generate_page_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="⬅", style=discord.ButtonStyle.primary, row=0)
    async def previous_page_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
        await self.update_view(interaction)

    @discord.ui.button(label="X", style=discord.ButtonStyle.danger, row=0)
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.delete()

    @discord.ui.button(label="➡", style=discord.ButtonStyle.primary, row=0)
    async def next_page_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
        await self.update_view(interaction)


# ==============================================================================
# VISTA PRINCIPAL DE AYUDA (PANTALLA DE INICIO)
# ==============================================================================
class HelpView(discord.ui.View):
    def __init__(self, bot: commands.Bot, categories: list[str]):
        super().__init__(timeout=180)
        self.bot = bot
        self.categories = categories
        self.initial_embed: Optional[discord.Embed] = None

        # Añadimos los botones y el menú de selección
        self.add_item(discord.ui.Button(
            label="Mirar en la web",
            style=discord.ButtonStyle.link,
            url="https://ejemplo.com",  # Reemplaza con tu URL
            row=0
        ))
        self.add_item(CategorySelect(self.categories))
        self.add_item(self.CloseButton(row=0))

    class CloseButton(discord.ui.Button):
        def __init__(self, row: int):
            super().__init__(label="X", style=discord.ButtonStyle.danger, row=row)

        async def callback(self, interaction: discord.Interaction):
            await interaction.message.delete()


# ==============================================================================
# EL COG PRINCIPAL DE AYUDA
# ==============================================================================
class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # (Las funciones auxiliares como get_visible_categories, count_total_app_commands,
    # y format_categories no necesitan cambios, así que las he omitido por brevedad,
    # pero deben estar aquí en tu archivo final)
    def get_visible_categories(self) -> list[str]:
        visible_cogs = [name for name, cog in self.bot.cogs.items() if
                        name not in HIDDEN_COGS and cog.get_app_commands()]
        return sorted(visible_cogs)

    def count_total_app_commands(self) -> int:
        def recursive_count(commands_list):
            count = 0
            for cmd in commands_list:
                if isinstance(cmd, app_commands.Group):
                    count += recursive_count(cmd.commands)
                else:
                    count += 1
            return count

        return recursive_count(self.bot.tree.get_commands())

    def format_categories(self, categories: list[str]) -> str:
        if not categories: return "```\nNo hay categorías para mostrar.\n```"
        num_columns = 3
        per_column = math.ceil(len(categories) / num_columns)
        columns = [categories[i:i + per_column] for i in range(0, len(categories), per_column)]
        max_rows = len(columns[0]) if columns else 0
        for col in columns:
            col.extend([""] * (max_rows - len(col)))
        formatted_string = "```\n"
        for i in range(max_rows):
            row = "".join(f"{columns[j][i]:<15}" for j in range(len(columns)))
            formatted_string += row.rstrip() + "\n"
        return formatted_string + "```"

    @app_commands.command(name="help", description="Muestra la lista de comandos y categorías del bot.")
    async def help_command(self, interaction: discord.Interaction):
        visible_categories = self.get_visible_categories()
        total_commands = self.count_total_app_commands()

        embed = discord.Embed(title="Lista de categorías", color=0x2b2d31)
        description = (
            f"**Comandos de {self.bot.user.name}**\n\n"
            f"» **Menú de ayuda**\n"
            f"Tengo `{len(visible_categories)}` categorías y `{total_commands}` comandos para explorar.\n\n"
            f"» **Categorías**\n{self.format_categories(visible_categories)}\n\n"
            f"» **Enlaces útiles**\n[Github](https://ejemplo.com) | [Privacidad](https://ejemplo.com)"
        )
        embed.description = description
        embed.set_footer(text="© Xardax", icon_url=self.bot.user.display_avatar.url)

        view = HelpView(self.bot, visible_categories)
        view.initial_embed = embed

        await interaction.response.send_message(embed=embed, view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(Help(bot))