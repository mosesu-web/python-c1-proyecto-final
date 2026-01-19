"""
Modelo Centro

Define la tabla 'centros' en la base de datos y proporciona:

- Validación de datos usando JSON Schema.
- Conversión a diccionario.
"""

import os
import json
from typing import TypedDict, Any

from extensions import db
from sqlalchemy.orm import Mapped, mapped_column
from jsonschema import validate, ValidationError


class CentroDict(TypedDict):
    """
    Clase para la representación de un centro como diccionario.
    """

    id_centro: int
    nombre: str
    direccion: str


class Centro(db.Model):
    """
    Modelo SQLAlchemy para representar centros médicos.
    """

    __tablename__ = "centros"
    
    # Columnas de la tabla
    id_centro: Mapped[int] = mapped_column(db.Integer, primary_key= True)
    nombre: Mapped[str] = mapped_column(db.String(30), nullable= False)
    direccion: Mapped[str] = mapped_column(db.String(30), nullable= False)

    @classmethod
    def load_schema(cls) -> dict[str,Any]:
        """
        Carga el esquema JSON para validar la entrada de datos.

        Returns:
            dict: Esquema JSON
        """

        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schemas/centro_schema.json")
        with open(path, "r") as fr:
            return json.load(fr)
        
    @classmethod
    def check_schema(cls, data: dict[str,str]):
        """
        Valida que los datos proporcionados cumplan con el esquema JSON.

        Args:
            data (dict): Datos a validar

        Raises:
            ValidationError: Si los datos no cumplen el esquema.
        """

        try:
            validate(data, cls.load_schema())
        except ValidationError:
            raise ValidationError("Schema de request no válido")

    def to_dict(self) -> CentroDict:
        """
        Convierte la instancia del modelo a un diccionario.

        Returns:
            CentroDict: Diccionario con los campos id_centro, nombre y direccion.
        """

        return {"id_centro": self.id_centro,
                "nombre": self.nombre,
                "direccion": self.direccion}