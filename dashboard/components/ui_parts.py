# ui_parts.py
# ==============================================================================
# Componentes reutilizables de UI para NiceGUI en el dashboard de Diami.
# ==============================================================================

from nicegui import ui, app


def get_dark_mode_toggle_button():
    """Crea un botón que alterna entre modo oscuro y claro con ícono dinámico, enlazado al almacenamiento local."""
    dark_mode = ui.dark_mode().bind_value(app.storage.user, "dark_mode")

    icono_inicial = "dark_mode" if dark_mode.value else "light_mode"
    boton = ui.button(icon=icono_inicial).props("flat round color=white")

    def toggle():
        dark_mode.toggle()
        nuevo_icono = "dark_mode" if dark_mode.value else "light_mode"
        boton.props(f"icon={nuevo_icono}")

    boton.on("click", toggle)
    return boton


def get_language_selector():
    """Crea un botón con un menú de selección de idioma."""
    with ui.element().classes("relative"):
        ui.button(icon="flag", on_click=lambda: menu_lang.open()).props(
            "flat color=white no-caps"
        ).add_slot("default", "ES")
        with ui.menu() as menu_lang:
            ui.menu_item("Español (ES)")
            ui.menu_item("English (EN)")


def get_login_button():
    """Crea el botón de login estilizado."""
    return (
        ui.button("LOGIN", icon="person")
        .props("color=indigo-7 rounded-lg")
        .classes("font-semibold text-white px-4 py-2")
    )


def get_header(avatar_bot_path: str):
    """Renderiza el header de la página."""
    with ui.header().classes(
        "px-6 lg:px-16 py-4 flex justify-between items-center z-50 "
        "bg-[rgba(90,90,90,0.6)] dark:bg-[rgba(30,30,30,0.6)] "
        "backdrop-blur-md shadow-md border-b border-gray-500"
    ):
        with ui.row().classes("items-center gap-6"):
            with ui.avatar(color="rgba(0,0,0,0.1)").style(
                "box-shadow: 0 0 10px 2px rgba(255, 105, 180, 0.4)"
            ):
                ui.image(avatar_bot_path)

            ui.label("Diami").classes("text-2xl font-bold")

        with ui.row().classes("items-center gap-3"):
            get_language_selector()
            get_dark_mode_toggle_button()
            get_login_button()
