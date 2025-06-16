# app/schemas/feature_flags.py

def get_default_feature_flags() -> dict:
    """
    Retorna el diccionario que representa el estado por defecto
    de las funciones activables del bot.
    """
    return {
        "log_channel_enabled": False,           # Para logs de errores del bot
        "history_channel_enabled": False,       # Para logs de moderación (edits, deletes)
        "welcome_message_enabled": False,       # Para mensajes de bienvenida
        "feliz_jueves_task_enabled": False,     # Para la tarea periódica de "Feliz Jueves"
    }