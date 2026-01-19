"""
Modelo Usuario

Define la tabla 'usuarios' en la base de datos y proporciona:
- Validación de datos usando JSON Schema.
- Conversión a diccionario.
"""

import os
import json
from typing import TypedDict, Any

from extensions import db
from sqlalchemy.orm import Mapped, mapped_column
from jsonschema import validate, ValidationError


class UsuarioDict(TypedDict):
    """
    Clase para la representación de un usuario como diccionario.
    """

    id_usuario: int
    username: str
    password: str
    rol: str


class Usuario(db.Model):
    """
    Modelo SQLAlchemy para representar usuarios del sistema.
    """

    __tablename__ = "usuarios"

    # Columnas de la tabla
    id_usuario: Mapped[int] = mapped_column(db.Integer, primary_key= True)
    username: Mapped[str] = mapped_column(db.String(30), unique= True, nullable= False)
    password: Mapped[str] = mapped_column(db.String(30), nullable= False)
    rol: Mapped[str] = mapped_column(db.String(15), nullable= False)

    @classmethod
    def load_schema(cls, login: bool, password_change: bool) -> dict[str,Any]:
        """
        Carga el esquema JSON para validar la entrada de datos.

        Args:
            login (bool): Si True, carga el esquema de login.
            password_change (bool): Si True, carga el esquema de cambio de contraseña.
                                    Ignorado si login es True.

        Returns:
            dict: Esquema JSON cargado desde el archivo correspondiente.
        """

        if login:
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schemas/login_schema.json")
        elif password_change:
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schemas/password_change_schema.json")
        else:
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schemas/user_schema.json")
        with open(path, "r") as fr:
            return json.load(fr)
    
    @classmethod
    def check_schema(cls, data: dict[str, str], login: bool= False, password_change: bool= False):
        """
        Valida que los datos proporcionados cumplan con el esquema JSON.

        Args:
            data (dict): Datos a validar.
            login (bool): Indica si se valida para login.
            password_change (bool): Indica si se valida para cambio de contraseña.

        Raises:
            ValidationError: Si los datos no cumplen el esquema.
        """

        try:
            validate(data, cls.load_schema(login, password_change))
        except ValidationError:
            raise ValidationError("Schema de request no válido")

    def to_dict(self) -> UsuarioDict:
        """
        Convierte la instancia del modelo a un diccionario.

        Returns:
            UsuarioDict: Diccionario con los campos id_usuario, username, password y rol.
        """

        return {"id_usuario": self.id_usuario,
                "username": self.username,
                "password": self.password,
                "rol": self.rol}