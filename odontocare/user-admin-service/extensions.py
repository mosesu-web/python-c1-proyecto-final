"""
Inicialización de las extensiones necesarias para la app Flask.

Se inicializa la extensión de SQLAlchemy para la gestión de la
base de datos.
"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Clase base para los modelos de la base de datos
    """
    pass

# Inicialización de SQLAlchemy con el modelo base.
db = SQLAlchemy(model_class= Base)