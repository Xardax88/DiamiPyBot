from nicegui import ui
from components.header import Header
from components.footer import Footer


class HomePage:
    def __init__(self):
        # Eliminar padding por defecto de NiceGUI
        ui.query(".nicegui-content").classes("p-0 gap-0")

    def render(self):
        Header().render()
        self.landing_page()
        self.desc_section()
        self.ai_section()
        self.cta_section()
        Footer().render()

    # ---- Sección principal ----
    def landing_page(self):
        with ui.row().classes("w-full items-center mb-10 lg:mb-28"):
            with ui.column().classes(
                "mx-auto mt-10 flex max-w-7xl flex-col-reverse items-center px-4 lg:mt-28 lg:flex-row"
            ):
                with ui.column().classes("flex flex-1 flex-col lg:mr-[5rem]"):
                    ui.label("Tu elfa bibliotecaria en Discord").classes(
                        "text-center text-4xl font-bold lg:mb-6 lg:text-left lg:text-6xl"
                    )
                    ui.label("Chat, economía, juegos, utilidades y mucho más").classes(
                        "mb-6 text-center text-2xl text-foreground/70 lg:text-left"
                    )
                    with ui.row().classes("justify-center lg:justify-start gap-4 mt-4"):
                        ui.button("Invitame ahora", icon="fab fa-discord").props(
                            " color=orange-9 no-caps"
                        ).classes(
                            "inline-flex items-center justify-center whitespace-nowrap font-medium ring-offset-background "
                            "transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring "
                            "focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border "
                            "border-input bg-background hover:bg-accent hover:text-accent-foreground "
                            "active:bg-accent/80 h-11 rounded-md px-8 group relative"
                        )
                        ui.button("Gestionar servidores", icon="settings").props(
                            "outline no-caps color=grey-8"
                        ).classes(
                            "inline-flex items-center justify-center whitespace-nowrap font-medium ring-offset-background "
                            "transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring "
                            "focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border "
                            "border-input bg-background hover:bg-accent hover:text-accent-foreground "
                            "active:bg-accent/80 h-11 rounded-md px-8 group relative"
                        )
                with ui.column().classes("relative mb-10 lg:mb-0"):
                    ui.image("assets/diami_avatar.png").classes(
                        "w-[250px] h-[250px] lg:w-[400px] lg:h-[400px] rounded-full object-cover"
                    ).style(
                        "box-shadow: 0 0 60px 10px rgba(255, 105, 180, 0.4); transition: transform 0.3s ease-in-out;"
                    )

    # ---- Sección de descripción ----
    def desc_section(self):
        with ui.column().classes(
            "w-full items-center gap-6 py-24 bg-[#e0e0e0] text-center dark:bg-[#101010]"
        ):
            with ui.column().classes("mx-auto max-w-7xl px-4 py-12"):
                ui.label(
                    "Diami es la nueva encarnación del bot de El Diagrama, esta vez escrito completamente en Python 🐍."
                ).classes("text-3xl font-bold lg:text-4xl dark:text-white")
                ui.label(
                    "Creada para El Diagrama y comunidades de Discord que quieran sumarla."
                ).classes(
                    "text-grey-500 mx-auto mt-4 max-w-2xl text-lg text-foreground/70 dark:text-gray-400"
                )
                with ui.row().classes(
                    "grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-4"
                ):
                    features = [
                        (
                            "favorite",
                            "Compañera Adorable",
                            "Disfruta de la compañía de una amigable elfa que llena de alegría tu servidor",
                        ),
                        (
                            "code",
                            "Slash Commands",
                            "Utiliza comandos slash para interactuar fácilmente con Diami",
                        ),
                        (
                            "gamepad",
                            "Economía y Juegos",
                            "Participa en juegos y actividades con tus amigos",
                        ),
                        (
                            "auto_graph",
                            "Funciones Innovadoras",
                            "En constante evolución con nuevas capacidades y mejoras",
                        ),
                    ]
                    for icon, title, desc in features:
                        with ui.card().tight().classes(
                            "bg-[#f5f5f5] dark:bg-[#050505] w-[250px] h-[200px] text-white p-6 rounded-xl shadow-md hover:scale-105 transition-transform"
                        ):
                            ui.icon(icon).classes("text-pink-400 text-4xl mb-4")
                            ui.label(title).classes("font-bold text-lg mb-2")
                            ui.label(desc).classes("text-sm text-gray-400")

    def features_section(self):
        with ui.column().classes("w-full flex justify-center"):
            with ui.column().classes(
                "relative flex max-w-7xl flex-col py-20 lg:items-center"
            ):
                with ui.column().classes("mt-16 lg:mt-24"):
                    with ui.row().classes(
                        "flex flex-col items-center justify-center gap-x-24 px-4 sm:px-4 lg:flex-row"
                    ):
                        with ui.column().classes(
                            "relative mb-8 flex w-full flex-1 justify-center lg:mb-0"
                        ):
                            ui.label("Bienvenidas")
                            ui.label(
                                "Diami puede personalizar su mensaje de bienvenida. "
                                "Tines varias variables disponibles y opciones diferentes."
                            )
                        with ui.column().classes(
                            "flex flex-1 flex-col items-center px-4 lg:items-start lg:px-0"
                        ):
                            ui.image()

    # ---- Sección de IA ----
    def ai_section(self):
        with ui.column().classes("w-full py-32 items-center text-center ml-5"):
            with ui.column().classes(
                "max-w-3xl mx-auto mt-6 gap-4 items-center text-center"
            ):
                ui.label("Un miembro más").classes(
                    "text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-orange-500 to-purple-500"
                )
                ui.label("Integra un sistema de IA").classes(
                    "text-gray-400 text-md md:text-lg"
                )
                ui.label(
                    "Diami puede interactuar como si fuera una usuario más. "
                    "Responde a mensajes, reacciona a publicaciones y participa en conversaciones. "
                    "Puedes mencionarla directamente para que responda a tus preguntas o te ayude con tareas específicas. "
                    "Su personalidad amigable aun que algo sarcastica y su capacidad para adaptarse a diferentes "
                    "contextos la convierten en una compañera ideal para tu servidor. "
                    "Se adapta y aprende de las interacciones con los usuarios, lo que la hace cada vez más útil y entretenida."
                ).classes("text-gray-400 text-md md:text-lg")

    # ---- Sección de llamada a la acción ----
    def cta_section(self):
        with ui.column().classes(
            "w-full py-32 items-center text-center bg-gradient-to-br from-[#121212] to-[#1b1b1b] m-0 p-0"
        ):
            with ui.column().classes(
                "max-w-3xl mx-auto mt-6 gap-4 items-center text-center"
            ):
                ui.label("\u00bfListo para invitarme fírimar?").classes(
                    "text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-orange-900 to-purple-500"
                )
                ui.label(
                    # "Saludos, mortales. Soy Diami, elfa bibliotecaria y miembro del staff de 'El Diagrama'. "
                    # "Si te cruzás conmigo, probablemente me encuentres entre libros antiguos, debates sobre RPGs, "
                    # "o simplemente disfrutando de un buen café negro. Soy más vieja que la mayoría de los problemas "
                    # "que existen por acá, pero eso no significa que no me mantenga al tanto de las últimas novedades "
                    # "geek. Si necesitás una mano, o simplemente querés charlar, no dudes en contactarme. Namárië"
                    "¿Querés llevarme a tu propio rincón del internet? ¡Excelente idea! Dale al botón y "
                    "preparate para un poco de sabiduría élfica, sarcasmo afilado y, por supuesto, una buena dosis "
                    "de cultura geek. Eso sí, yrch, no me esperes para hacer el trabajo sucio. Hannon le por la "
                    "invitación, y espero que nos veamos por ahí."
                ).classes("text-gray-400 text-md lg:text-left")
                ui.button("Invitame a Discord", icon="fab fa-discord").props(
                    "outline color=orange-9"
                ).classes("mt-6 px-6 py-3 text-white rounded-lg text-lg font-semibold")
