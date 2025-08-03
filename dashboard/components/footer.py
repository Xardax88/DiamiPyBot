# dashboard/components/footer.py
from nicegui import ui


class Footer:
    def render(self):
        with ui.column().classes(
            "w-full bg-[#0e0e0e] text-white px-6 lg:px-20 py-16 gap-12"
        ):
            with ui.row().classes(
                "mx-auto max-w-[1240px] justify-between flex-wrap gap-8"
            ):
                with ui.column().classes("max-w-xs gap-3"):
                    with ui.row().classes("items-center gap-2"):
                        ui.image("assets/diami_avatar.png").classes(
                            "w-8 h-8 rounded-full"
                        )
                        ui.label("Diami").classes("text-xl font-bold")
                    ui.label(
                        "Una bot que busca incentivar el conocimiento y la actividad en tu servidor."
                    ).classes("text-sm text-gray-400")
                    with ui.row().classes("gap-3 mt-4"):
                        ui.button("Invitar", icon="fab fa-discord").props(
                            "color=pink"
                        ).classes("text-black px-4 py-2 font-semibold rounded-md")
                        ui.button("Soporte", icon="chat").props(
                            "flat color=white"
                        ).classes("text-sm")
                with ui.row().classes("gap-16 flex-wrap"):
                    for section, items in [
                        ("Recursos", ["Github", "Estado"]),
                        ("Diami", ["Soporte", "Sugerencias", "Reportes"]),
                        ("Legal", ["Términos de uso", "Privacidad"]),
                    ]:
                        with ui.column().classes("gap-1 text-sm"):
                            ui.label(section).classes("font-bold text-white mb-2")
                            for item in items:
                                ui.link(item, "#").classes(
                                    "text-gray-400 hover:text-white"
                                )
            ui.separator().classes("mx-auto max-w-[1240px] my-6 border-white/10")
            with ui.row().classes("w-full justify-center"):
                ui.label("© Xardax, 2025. Todos los derechos reservados.").classes(
                    "text-xs text-gray-500 text-center"
                )
