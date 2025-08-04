# app/schemas/level.py


def get_default_user_level(guild_id: int, user_id: int) -> dict:
    """
    Retorna la estructura por defecto para el documento de experiencia de un usuario en un servidor.
    """
    return {"guild_id": guild_id, "user_id": user_id, "xp": 0}
