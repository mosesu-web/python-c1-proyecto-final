"""
Modelo Doctor

Define la tabla 'doctores' en la base de datos y proporciona:
- Validación de datos usando JSON Schema.
- Conversión a diccionario.
"""

import os
import json
from typing import TypedDict, Any

from extensions import db
from sqlalchemy.orm import Mapped, mapped_column
from jsonschema import validate, ValidationError


class DoctorDict(TypedDict):
    """
    Clase para la representación de un doctor como diccionario.
    """

    id_doctor: int
    id_usuario: int
    nombre: str
    apellido: str
    especialidad: str


class Doctor(db.Model):
    """
    Modelo SQLAlchemy para representar doctores.
    """

    __tablename__ = "doctores"

    # Columnas de la tabla
    id_doctor: Mapped[int] = mapped_column(db.Integer, primary_key= True)
    id_usuario: Mapped[int] = mapped_column(db.Integer,  nullable= True)
    nombre: Mapped[str] = mapped_column(db.String(30), nullable= False)
    apellido: Mapped[str] = mapped_column(db.String(30), nullable= False)
    especialidad: Mapped[str] = mapped_column(db.String(30), nullable= False)

    @classmethod
    def load_schema(cls, update: bool) -> dict[str,Any]:
        """
        Carga el esquema JSON para validar la entrada de datos.

        Args:
            update (bool): Si True, carga el esquema para actualización; 
                           si False, para creación.

        Returns:
            dict: Esquema JSON cargado desde archivo correspondiente.
        """

        if update:
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schemas/update_doctor_schema.json")
        else:    
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schemas/doctor_schema.json")
        with open(path, "r") as fr:
            return json.load(fr)
    
    @classmethod
    def check_schema(cls, data: dict[str,str], update: bool= False):
        """
        Valida que los datos proporcionados cumplan con el esquema JSON.

        Args:
            data (dict): Datos a validar
            update (bool): Indica si la validación es para actualización

        Raises:
            ValidationError: Si los datos no cumplen el esquema.
        """

        try:
            validate(data, cls.load_schema(update))
        except ValidationError:
            raise ValidationError("Schema de request no válido")

    def to_dict(self) -> DoctorDict:
        """
        Convierte la instancia del modelo a un diccionario.

        Returns:
            DoctorDict: Diccionario con los campos id_doctor, id_usuario, nombre, apellido y especialidad.
        """
        return {"id_doctor": self.id_doctor,
                "id_usuario": self.id_usuario,
                "nombre": self.nombre,
                "apellido": self.apellido,
                "especialidad": self.especialidad}