"""
Modelo Paciente

Define la tabla 'pacientes' en la base de datos y proporciona:
- Validación de datos usando JSON Schema.
- Conversión a diccionario.
"""

import os
import json
from typing import TypedDict, Any

from extensions import db
from sqlalchemy.orm import Mapped, mapped_column
from jsonschema import validate, ValidationError

class PacienteDict(TypedDict):
    """
    Clase para la representación de un paciente como diccionario.
    """

    id_paciente: int
    id_usuario: int
    nombre: str
    apellido: str
    telefono: int
    estado: bool


class Paciente(db.Model):
    """
    Modelo SQLAlchemy para representar pacientes.
    """

    __tablename__ = "pacientes"
    
    # Columnas de la tabla
    id_paciente: Mapped[int] = mapped_column(db.Integer, primary_key= True)
    id_usuario: Mapped[int] = mapped_column(db.Integer, nullable= True)
    nombre: Mapped[str] = mapped_column(db.String(30), nullable= False)
    apellido: Mapped[str] = mapped_column(db.String(30), nullable= False)
    telefono: Mapped[int] = mapped_column(db.Integer, nullable= False)
    estado: Mapped[bool] = mapped_column(db.String(10), nullable= False)

    @classmethod
    def load_schema(cls, update: bool)  -> dict[str,Any]:
        """
        Carga el esquema JSON para validar la entrada de datos.

        Args:
            update (bool): Si True, carga el esquema para actualización; 
                           si False, para creación.

        Returns:
            dict: Esquema JSON cargado desde archivo correspondiente.
        """

        if update:
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schemas/update_paciente_schema.json")
        else:    
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schemas/paciente_schema.json")
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

    def to_dict(self) -> PacienteDict:
        """
        Convierte la instancia del modelo a un diccionario.

        Returns:
            PacienteDict: Diccionario con los campos id_paciente, id_usuario, nombre, apellido, telefono y estado.
        """
        return {"id_paciente": self.id_paciente,
                "id_usuario": self.id_usuario,
                "nombre": self.nombre,
                "apellido": self.apellido,
                "telefono": self.telefono,
                "estado": self.estado}