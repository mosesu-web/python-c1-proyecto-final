"""
Funciones para generar y decoficar tokens.
Se utilizan para autenticación y autorización.
"""

import jwt
from datetime import datetime, timezone
from config import Config
from typing import Tuple

def token_generator(id: int, user_role: str) -> Tuple[str, datetime]:
    """
    Genera un token para un usuario dado.

    Args:
        id (int): ID del usuario.
        user_role (str): Rol del usuario.

    Returns:
        Tuple[str, datetime]: Token y fecha de expiración.
    """

    now: datetime = datetime.now(timezone.utc)  # Fecha actual en formato UTC
    expiration = now + Config.JWT_EXPIRATION_DELTA # Fecha de expiración
    payload: dict[str, str|int|datetime] = {
                                            "id": id,
                                            "role": user_role,
                                            "iat": now,
                                            "exp": expiration
                                            }
    return (jwt.encode(payload,
                      Config.JWT_SECRET_KEY,
                      algorithm= "HS256"),
                      expiration)

def token_decoder(token: str) -> dict[str, str|int|datetime]:
    """
    Decodifica un token. Valida su integridad y si ya ha expirado.

    Args:
        token (str): Token a decodificar.

    Returns:
        dict[str, str | int | datetime]: Payload decodificado del token.

    Raises:
        jwt.InvalidTokenError: Si el token no es válido.
        jwt.ExpiredSignatureError: Si el token ha expirado.
    """

    try:
        return jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=["HS256"])
    except jwt.InvalidTokenError:
        raise jwt.InvalidTokenError("Token invalido")
    except jwt.ExpiredSignatureError:
        raise jwt.ExpiredSignatureError("El token ha expirado")