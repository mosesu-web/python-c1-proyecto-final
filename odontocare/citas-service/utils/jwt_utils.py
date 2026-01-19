"""
Funciones para generar y decoficar tokens.
Se genera un token que se actualiza automaticamente
antes de que caduque. Se usa para garantizar el acceso a
los endpoints del servicio autenticacion y admin.
"""

import jwt
from datetime import datetime, timedelta, timezone
from config import Config, UserRoles
from dataclasses import dataclass, field

@dataclass
class ServiceTokenManager:
    """
    Clase para generar y gestionar tokens de servicios internos.

    Atributos:
        delta (int): Número de segundos antes de la expiración para renovar el token automáticamente.
        _expiration (datetime): Fecha y hora de expiración del token actual.
        _token (str): Token actual.

    Métodos:
        get_token(user_role: str = "") -> str:
            Devuelve el token actual si es válido o genera uno nuevo si está próximo a caducar.
    """
    delta: int
    _expiration: datetime = field(init= False)
    _token: str = field(default= "", init=False)

    def get_token(self, user_role: str= "") -> str:
        """
        Devuelve un token válido para servicios internos.
        Si el token actual está próximo a expirar (según `delta`),
        genera uno nuevo automáticamente.

        Este token es diferente al generado al hacer login un usuario,
        contiene campos diferentes:
            role(str): rol de servicio, para identificar peticiones internas.
            rol_usuario(str): rol del usuario que hace la petición al servicio
            gestión de citas.

        Args:
            user_role (str): Rol del usuario que hace la petición a traves del servicio.

        Returns:
            str: Token codificado.
        """
        now: datetime = datetime.now(timezone.utc)

        # Si existe token y aún no está cerca de caducar, se retorna
        if self._token and now > self._expiration - timedelta(seconds= self.delta):
            return self._token
        
        # Se genera un token nuevo
        expiration: datetime = now + Config.JWT_EXPIRATION_DELTA
        payload: dict[str, str|datetime] = {"role": UserRoles.SERVICE,  # Rol fijo de servicios internos
                                            "user_role": user_role,  # Rol de usuario (opcional)
                                            "iat": now,  # Fecha de emisión
                                            "exp": expiration  # Fecha de expiración
                                            }
        
        token: str = jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm= "HS256")
        self._token = token
        self._expiration = expiration
        return token

def token_decoder(token: str) -> dict[str, str | int | datetime]:
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
    
