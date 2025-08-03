# app/schemas/guild_config.py
from .feature_flags import get_default_feature_flags


# ==============================================================================
# Esquema de configuración del servidor (guild)
# ==============================================================================
def get_default_guild_config(guild_id: int) -> dict:
    """
    Retorna el diccionario que representa el schema por defecto para la configuración
    de un nuevo servidor (guild) en la base de datos.

    Args:
        guild_id (int): El ID del servidor que actuará como _id del documento.
    """
    return {
        "_id": guild_id,
        "main_channel_id": None,
        "log_channel_id": None,
        "rules_channel_id": None,
        "history_channel_id": None,
        "confession_channel_id": None,
        "report_channel_id": None,
        "suggestion_channel_id": None,
        "features": get_default_feature_flags(),
    }
