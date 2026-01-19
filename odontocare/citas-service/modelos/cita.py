"""
Modelo Cita

Define la tabla 'citas' en la base de datos y proporciona:
- Validación de datos usando JSON Schema según el rol y tipo de query.
- Conversión a diccionario.
"""
import os
import json
from datetime import datetime
from typing import TypedDict, Any

from extensions import db
from sqlalchemy.orm import Mapped, mapped_column
from jsonschema import validate, ValidationError
from config import UserRoles


class CitaDict(TypedDict):
    """
    Clase para la representación de una cita como diccionario.
    """

    id_cita: int
    fecha: datetime
    motivo: str
    estado: bool
    id_paciente: int
    id_doctor: int
    id_centro: int
    id_usuario_registra: int


class Cita(db.Model):
    """
    Modelo SQLAlchemy para representar citas médicas.
    """

    __tablename__ = "citas"
    
    # Columnas de la tabla
    id_cita: Mapped[int] = mapped_column(db.Integer, primary_key= True)
    fecha: Mapped[datetime] = mapped_column(db.DateTime, nullable= False)
    motivo: Mapped[str] = mapped_column(db.String(100), nullable= False)
    estado: Mapped[str] = mapped_column(db.String, nullable= False)
    id_paciente: Mapped[int] = mapped_column(db.Integer, nullable= False)
    id_doctor: Mapped[int] = mapped_column(db.Integer, nullable= False)
    id_centro: Mapped[int] = mapped_column(db.Integer, nullable= False)
    id_usuario_registra: Mapped[int] = mapped_column(db.Integer, nullable= False)

    @classmethod
    def load_schema(cls, rol: str, query: bool) -> dict[str,Any]:
        """
        Carga el esquema JSON según el rol y tipo de consulta.

        Args:
            rol (str): Rol del usuario que realiza la acción.
            query (bool): Si True, carga esquema de query; si False, esquema de creación.

        Returns:
            dict: Esquema JSON cargado desde el archivo correspondiente.
        """

        if not query:
            if rol == UserRoles.PACIENTE:
                path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schemas/paciente_cita_schema.json")
            elif rol == UserRoles.ADMIN:
                path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schemas/admin_cita_schema.json")
        else:
            if rol == UserRoles.ADMIN:
                path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schemas/admin_cita_query_schema.json")
            elif rol == UserRoles.SECRETARIA:
                path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schemas/secretaria_cita_query_schema.json")    
        with open(path, "r") as fr:
            return json.load(fr)
    
    @classmethod
    def check_schema(cls, data: dict[str,str], rol: str, query: bool= False):
        """
        Valida que los datos proporcionados cumplan con el esquema JSON según rol y tipo de consulta.

        Args:
            data (dict): Datos a validar.
            rol (str): Rol del usuario que realiza la acción.
            query (bool): Si True, valida esquema de query; si False, esquema de creación.

        Raises:
            ValidationError: Si los datos no cumplen el esquema.
        """

        try:
            validate(data, cls.load_schema(rol, query))
        except ValidationError:
            raise ValidationError("Schema de request no válido")

    def to_dict(self) -> CitaDict:
        """
        Convierte la instancia del modelo a un diccionario.

        Returns:
            CitaDict: Diccionario con los campos de la cita.
        """

        return {"id_cita": self.id_cita,
                "fecha": datetime.isoformat(self.fecha) + "Z",
                "motivo": self.motivo,
                "estado": self.estado,
                "id_paciente": self.id_paciente,
                "id_doctor": self.id_doctor,
                "id_centro": self.id_centro,
                "id_usuario_registra": self.id_usuario_registra
            }