"""
Define la creación de la app de Flask. Configura la base de datos
y registra los blueprints de autenticación y administración.
"""

from flask import Flask
from recursos import auth_bp, admin_bp
from config import Config
from extensions import db


def create_app():
    """
    Crea y configura la app de Flask.

    Configura la base de datos.
    Registra los blueprints.
    """

    app = Flask(__name__)
    
    # Configuración de la base de datos
    app.config["SQLALCHEMY_DATABASE_URI"] = Config.SQLALCHEMY_DB_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = Config.SQLALCHEMY_TRACK_MODIFICATIONS

    # Inicializa la extension de SQLAlchemy
    db.init_app(app)

    # Crea todas las tablas definidas en los modelos si no existen
    with app.app_context():
        db.create_all()

    # Registra los blueprints con prefijo
    app.register_blueprint(auth_bp, url_prefix="/api/v1")  # Autenticación
    app.register_blueprint(admin_bp, url_prefix="/api/v1")  # Administración
  
    return app