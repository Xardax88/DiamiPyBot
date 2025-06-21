# ==============================================================================
# dashboard/index.py
# ------------------------------------------------------------------------------
# Punto de entrada principal para la interfaz web de Diami Bot usando NiceGUI.
# Gestiona rutas, autenticación OAuth2 con Discord y renderizado de páginas.
#
# Autor: Xardax
# Proyecto: DiamiBot
# Fecha: 2025
# ==============================================================================

from nicegui import ui, app
from starlette.responses import RedirectResponse
from starlette.requests import Request
from datetime import datetime, timedelta
from requests_oauthlib import OAuth2Session
import os
import jwt
from dotenv import load_dotenv

# from utils.auth import get_user_data_from_token
from pages.home import HomePage

# from pages.dashboard import DashboardPage

# ------------------------------------------------------------------------------
# Configuración del entorno
# ------------------------------------------------------------------------------
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
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
# Funciones
# ==============================================================================
def get_user_data_from_token(token: str):
    try:
        return jwt.decode(token, SESSION_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None


# ------------------------------------------------------------------------------
# Rutas principales
# ------------------------------------------------------------------------------
@ui.page("/")
async def home(request: Request):
    HomePage().render()


@ui.page("/dashboard")
async def dashboard(request: Request):
    token = request.session.get("token")
    user = get_user_data_from_token(token)
    if not user:
        return RedirectResponse("/")
    # DashboardPage(request, user).render()


# ------------------------------------------------------------------------------
# Autenticación OAuth2
# ------------------------------------------------------------------------------
@ui.page("/oauth/callback")
async def oauth_callback(request: Request):
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


@ui.page("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/")


# ==============================================================================
# Iniciar la aplicación NiceGUI
# ==============================================================================

ui.run(storage_secret=SESSION_SECRET, title="Diami Py Bot")
