# dashboard/dash.py
"""
Dashboard para Discord usando NiceGUI y OAuth2

"""

from nicegui import ui, app
from starlette.requests import Request
from starlette.responses import RedirectResponse
from datetime import datetime, timedelta
import os
import jwt
from dotenv import load_dotenv
from requests_oauthlib import OAuth2Session

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# ==============================================================================
# Variables de entorno
# ==============================================================================
load_dotenv()
CLIENT_ID = os.getenv("OAUTH_CLIENT_ID")
CLIENT_SECRET = os.getenv("OAUTH_CLIENT_SECRET")
REDIRECT_URI = os.getenv("OAUTH_REDIRECT_URI")
SESSION_SECRET = os.getenv("SESSION_SECRET_KEY")
AUTHORIZATION_URL = "https://discord.com/api/oauth2/authorize"
TOKEN_URL = "https://discord.com/api/oauth2/token"
API_BASE_URL = "https://discord.com/api/v10"
SCOPES = ["identify", "guilds"]

# ==============================================================================
# Configuración de la interfaz NiceGUI
# ==============================================================================
ui.page_title("Diami Py Bot")

ui.add_body_html(
    """
<script>
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    if (localStorage.getItem('user.dark_mode') === null) {
        localStorage.setItem('user.dark_mode', prefersDark ? 'true' : 'false');
    }
</script>
"""
)


# ==============================================================================
# Funciones de utilidad
# ==============================================================================
def get_user_data_from_token(token: str):
    try:
        return jwt.decode(token, SESSION_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None


# ==============================================================================
# Recursos
# ==============================================================================

# ---- Ruta del avatar de Diami ----
avatar_bot = "assets/diami_avatar.png"


# ---- Botón de modo oscuro con ícono dinámico ----
def dark_mode_toggle_button():
    """Crea un botón que alterna entre modo oscuro y claro con ícono dinámico."""
    dark_mode = ui.dark_mode().bind_value(app.storage.user, "dark_mode")

    # Definir el ícono inicial según el modo actual
    icono_inicial = "dark_mode" if dark_mode.value else "light_mode"

    # Crear el botón con ícono
    boton = ui.button(icon=icono_inicial, on_click=lambda: toggle()).props(
        "flat round color=white"
    )

    # Función de alternancia que también cambia el ícono
    def toggle():
        dark_mode.toggle()
        nuevo_icono = "dark_mode" if dark_mode.value else "light_mode"
        boton.props(f"icon={nuevo_icono}")

    return boton


# ==============================================================================
# Rutas de la aplicación
# ==============================================================================


# ---- Página de inicio ----
@ui.page("/")
async def home(request: Request):
    """
    token = request.session.get("token")
    if token and get_user_data_from_token(token):
        return RedirectResponse("/dashboard")

    with ui.column().classes("absolute-center items-center gap-4"):
        ui.label("Bienvenido").classes("text-h4")
        ui.button("Login con Discord", on_click=lambda: ui.navigate.to("/login"))
    """
    """
    Página de inicio del bot. Muestra un mensaje de bienvenida y un botón de login.
    Si el usuario ya está autenticado, redirige al dashboard.
    """
    header()
    landing_page()


# ---- Página del Dashboard ----
@ui.page("/dashboard")
async def dashboard(request: Request):
    token = request.session.get("token")
    user = get_user_data_from_token(token)
    if not user:
        return RedirectResponse("/")

    with ui.column().classes("absolute-center"):
        ui.label(f"Hola, {user['name']}").classes("text-h4")
        ui.button("Logout", on_click=lambda: ui.navigate.to("/logout"))


# ==============================================================================
# Control de autenticación OAuth2 y manejo de sesiones
# ==============================================================================


# ---- Callback de OAuth2 ----
@ui.page("/oauth/callback")
async def oauth_callback(request: Request):
    """
    Maneja el callback de OAuth2 después de que el usuario autoriza la aplicación.
    """
    if request.query_params.get("state") != request.session.pop("oauth_state", None):
        return "Error de estado", 400

    session = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI, scope=SCOPES)
    token = session.fetch_token(
        TOKEN_URL,
        client_secret=CLIENT_SECRET,
        authorization_response=str(request.url),
    )
    user_info = session.get(f"{API_BASE_URL}/users/@me").json()
    payload = {
        "id": user_info["id"],
        "name": user_info["username"],
        "exp": datetime.utcnow() + timedelta(days=1),
    }
    session_token = jwt.encode(payload, SESSION_SECRET, algorithm="HS256")
    request.session["token"] = session_token
    return RedirectResponse("/dashboard")


# ---- Ruta de login ----
@app.get("/login")
def login(request: Request):
    """
    Inicia el proceso de autenticación OAuth2 redirigiendo al usuario a Discord.
    Guarda el estado en la sesión para verificarlo en el callback.
    """
    oauth = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI, scope=SCOPES)
    url, state = oauth.authorization_url(AUTHORIZATION_URL)
    request.session["oauth_state"] = state
    return RedirectResponse(url)


# ---- Ruta de logout ----
@ui.page("/logout")
async def logout(request: Request):
    """
    Cierra la sesión del usuario eliminando el token de la sesión.
    Redirige al usuario a la página de inicio.
    """
    request.session.clear()
    return RedirectResponse("/")


# ==============================================================================
# Header del sitio
# ==============================================================================
def header():
    """
    Header superior del sitio.
    """
    with ui.header().classes(
        "px-6 lg:px-16 py-4 flex justify-between items-center z-50 "
        "bg-[rgba(90,90,90,0.6)] dark:bg-[rgba(30,30,30,0.6)] "
        "backdrop-blur-md shadow-md shadow-md border-b border-gray-500"
    ):

        # ---- Sección Izquierda: Logo + Menú ----
        with ui.row().classes("items-center gap-6"):

            # Logo del bot
            with ui.avatar(color="rgba(0,0,0,0.1)").style(
                "box-shadow: 0 0 10px 2px rgba(255, 105, 180, 0.4)"
            ):
                ui.image(avatar_bot)

            ui.label("Diami").classes("text-2xl font-bold text-black dark:text-white")

            # Menú de navegación
            """
            ui.link("COMANDOS", "#comandos").classes(
                "text-white hover:text-pink-40 text-sm font-semibold"
            )
            ui.link("RECURSOS", "#recursos").classes(
                "text-white hover:text-pink-40 text-sm font-semibold"
            )
            """

        # ---- Sección Derecha: Idioma, Modo oscuro y Login ----
        with ui.row().classes("items-center gap-3"):

            # Selector de idioma
            with ui.element().classes("relative"):
                ui.button(icon="flag", on_click=lambda: menu_lang.open()).props(
                    "flat color=white no-caps"
                ).add_slot("default", "ES")
                with ui.menu() as menu_lang:
                    ui.menu_item("Español (ES)")
                    ui.menu_item("English (EN)")

            # Modo oscuro

            dark_mode_toggle_button()

            # Botón de login con estilo
            ui.button("LOGIN", icon="person").props(
                "color=indigo-7 rounded-lg"
            ).classes("font-semibold text-white px-4 py-2")


# ==============================================================================
# Página de bienvenida del bot
# ==============================================================================
def landing_page():
    """
    Página de bienvenida del bot.
    """
    # -- Sección principal de bienvenida con imagen de fondo --
    ui.query(".nicegui-content").classes("p-0 gap-0")
    with ui.row().classes(
        # "w-full min-h-screen items-center justify-center p-6 lg:p-16 flex-wrap-reverse lg:flex-nowrap p-0"
        "w-full items-center mb-10 lg:mb-28"
    ):

        with ui.column().classes(
            "mx-auto mt-10 flex max-w-7xl flex-col-reverse items-center px-4 lg:mt-28 lg:flex-row"
        ):
            with ui.column().classes("flex flex-1 flex-col lg:mr-[5rem]"):
                # Título principal
                ui.label("La bibliotecaria de").classes(
                    "text-center text-4xl font-bold lg:mb-6 lg:text-left lg:text-6xl"
                )
                ui.label("El Diagrama").classes(
                    "text-center text-4xl font-bold lg:mb-6 lg:text-left lg:text-6xl"
                )
                # Subtítulo descriptivo
                ui.label("Chat, economía, juegos, utilidades y mucho más").classes(
                    "mb-6 text-center text-2xl text-foreground/70 lg:text-left"
                )
                # Botones de acción
                with ui.row().classes("justify-center lg:justify-start gap-4 mt-4"):
                    ui.button("Añadir a la bot", icon="fab fa-discord").props(
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

            # Sección de avatar (columna derecha en desktop)
            with ui.column().classes("relative mb-10 lg:mb-0"):
                # Imagen del avatar del bot con estilo glow
                ui.image(avatar_bot).classes(
                    "w-[250px] h-[250px] lg:w-[400px] lg:h-[400px] rounded-full object-cover"
                ).style(
                    "box-shadow: 0 0 60px 10px rgba(255, 105, 180, 0.4); transition: transform 0.3s ease-in-out;"
                )

    trust_section()
    ai_section()
    cta_section()
    footer()


# ---- Sección de Características ----
def trust_section():
    with ui.column().classes(
        "w-full items-center gap-6 py-24 bg-[#e0e0e0] text-center dark:bg-[#101010]"
    ):
        with ui.column().classes("mx-auto max-w-7xl px-4 py-12"):
            with ui.column().classes("mb-10 text-center"):
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


# ---- Sección de Personalidad ----
def ai_section():
    with ui.column().classes("w-full py-32 items-center text-center ml-5"):
        with ui.column().classes(
            "max-w-3xl mx-auto mt-6 gap-4 items-center text-center"
        ):
            ui.label("Un miembro mas").classes(
                "text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-pink-500 to-purple-500"
            )
            ui.label("Integra un sistema de IA").classes(
                "text-gray-400 text-md md:text-lg"
            )

            ui.label(
                "Diami puede interactuar como si fuera una usuario mas. "
                "Responde a mensajes, reacciona a publicaciones y participa en conversaciones. "
                "Puedes mencionarla directamente para que responda a tus preguntas o te ayude con tareas específicas. "
                "Su personalidad amigable y su capacidad para adaptarse a diferentes contextos la convierten en una compañera ideal para tu servidor. "
                "Se adapta y aprende de las interacciones con los usuarios, lo que la hace cada vez más útil y entretenida."
            ).classes("text-gray-400 text-md md:text-lg")


# ---- Sección de CTA ----
def cta_section():
    with ui.column().classes(
        "w-full py-32 items-center text-center bg-gradient-to-br from-[#121212] to-[#1b1b1b] m-0 p-0"
    ):
        ui.label("¿Listo fírimar?").classes(
            "text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-pink-500 to-purple-500"
        )

        ui.button("Añadir a la bot", icon="fab fa-discord").props(
            "outline color=pink"
        ).classes("mt-6 px-6 py-3 text-white rounded-lg text-lg font-semibold")


# ---- Sección de Footer ----
def footer():
    with ui.column().classes(
        "w-full bg-[#0e0e0e] text-white px-6 lg:px-20 py-16 gap-12"
    ):

        # Contenido principal
        with ui.row().classes("mx-auto max-w-[1240px] justify-between flex-wrap gap-8"):

            # Marca
            with ui.column().classes("max-w-xs gap-3"):
                with ui.row().classes("items-center gap-2"):
                    ui.image("assets/diami_avatar.png").classes("w-8 h-8 rounded-full")
                    ui.label("Diami").classes("text-xl font-bold")

                ui.label(
                    "Una bot que busca incentivar el conocimiento y la actividad en tu servidor."
                ).classes("text-sm text-gray-400")

                with ui.row().classes("gap-3 mt-4"):
                    ui.button("Invitar", icon="fab fa-discord").props(
                        "color=pink"
                    ).classes("text-black px-4 py-2 font-semibold rounded-md")
                    ui.button("Soporte", icon="chat").props("flat color=white").classes(
                        "text-sm"
                    )

            # Menú de enlaces
            with ui.row().classes("gap-16 flex-wrap"):
                for section, items in [
                    ("Recursos", ["Github", "Estado"]),
                    ("Diami", ["Soporte", "Sugerencias", "Reportes"]),
                    ("Legal", ["Términos de uso", "Privacidad"]),
                ]:
                    with ui.column().classes("gap-1 text-sm"):
                        ui.label(section).classes("font-bold text-white mb-2")
                        for item in items:
                            ui.link(item, "#").classes("text-gray-400 hover:text-white")

        # Separador
        ui.separator().classes("mx-auto max-w-[1240px] my-6 border-white/10")

        # Créditos finales
        with ui.row().classes("w-full justify-center"):
            ui.label("© Xardax, 2025. Todos los derechos reservados.").classes(
                "text-xs text-gray-500 text-center"
            )


# ==============================================================================
# Iniciar la aplicación NiceGUI
# ==============================================================================
ui.run(storage_secret=SESSION_SECRET, title="Diami Py Bot")
