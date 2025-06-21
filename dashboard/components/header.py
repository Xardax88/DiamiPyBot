# dashboard/components/header.py
from nicegui import ui
from .ui_parts import (
    get_dark_mode_toggle_button,
    get_language_selector,
    get_login_button,
)


class Header:
    def __init__(self, avatar_bot_path: str = "assets/diami_avatar.png"):
        self.avatar_bot_path = avatar_bot_path

    def render(self):
        with ui.header().classes(
            "sticky top-0 z-20 w-full border-b border-input bg-background/95 backdrop-blur "
            "bg-[rgba(90,90,90,0.6)] dark:bg-[rgba(30,30,30,0.6)] "
            "supports-[backdrop-filter]:bg-background/60"
        ):
            with ui.row().classes(
                "container mx-auto flex items-center justify-between px-0 h-9"
            ):
                with ui.row().classes("items-center gap-4"):
                    with ui.avatar(color="rgba(0,0,0,0.1)", size="2rem").style(
                        "box-shadow: 0 0 10px 2px rgba(255, 105, 180, 0.4)"
                    ):
                        ui.image(self.avatar_bot_path)
                    ui.label("Diami").classes(
                        "text-2xl font-bold text-gray-900 dark:text-gray-100"
                    )
                with ui.row().classes("items-center gap-2"):
                    get_language_selector()
                    get_dark_mode_toggle_button()
                    get_login_button()
