"""
Configuración de la app Flask para el servicio de autenticación y admin

Carga variables de entorno, configura el las variables modulo jwt_utils,
define la ruta para la db y el puerto y debug mode de la app de flask.
Define los roles de usuarios para validación de autorización.
"""

from dotenv import load_dotenv
from datetime import timedelta
import os

# Carga las variables de entorno desde .env
load_dotenv()


class Config:
    """
    Clase para la configuración principal de la app.

    Attributes:
        JWT_SECRET_KEY (str): Clave secreta para generar tokens.
        JWT_EXPIRATION_DELTA (timedelta): Tiempo de expiración de los tokens.
        SQLALCHEMY_DB_URI (str): URI de conexión a la base de datos SQLite.
        SQLALCHEMY_TRACK_MODIFICATIONS (bool): Configuración de seguimiento de cambios de SQLAlchemy.
        DEBUG (bool): Activación del modo debug en Flask.
        PORT (int): Puerto en el que se ejecuta la aplicación.
    """

    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
    JWT_EXPIRATION_DELTA: timedelta = timedelta(hours=1)
    SQLALCHEMY_DB_URI: str = f"sqlite:///{os.getenv('USERS_ADMIN_DB_PATH')}"
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    DEBUG: bool = os.getenv("FLASK_DEBUG") == "1"
    PORT: int = int(os.getenv("USERS_ADMIN_PORT"))


class UserRoles:
    """
    Clase para definir los roles de usuario.

    Attributes:
        ADMIN (str): Rol de administrador.
        MEDICO (str): Rol de médico.
        SECRETARIA (str): Rol de secretaria.
        PACIENTE (str): Rol de paciente.
        SERVICE (str): Rol de servicio interno,
        para las comunicaciones entre servicios.
    """

    ADMIN: str = "admin"
    MEDICO: str = "doctor"
    SECRETARIA: str = "secretariat"
    PACIENTE: str = "patient"
    SERVICE: str = "citas-service"