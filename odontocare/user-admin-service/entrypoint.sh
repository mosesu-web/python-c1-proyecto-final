#!/bin/bash
set -e

# Crea las tablas si no existen e incluye el usuario admin por defecto
# si no existe

python -c "
from app import create_app, db
from modelos import Usuario
import os
from dotenv import load_dotenv
from sqlalchemy import inspect

load_dotenv()

app = create_app()
with app.app_context():
    inspector = inspect(db.engine)
    if 'usuario' not in inspector.get_table_names():
        db.create_all()
    if not Usuario.query.first():
        admin = Usuario(username= os.getenv('DEFAULT_USER'), # usuario por defecto desde .env
            password= os.getenv('DEFAULT_PASSWORD'), # contraseña por defecto desde .env
            rol= 'admin'
        )
        db.session.add(admin)
        db.session.commit()
"

# Ejecuta el comando principal (CMD)
exec "$@"