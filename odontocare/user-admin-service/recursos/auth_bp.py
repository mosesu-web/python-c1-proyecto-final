"""
Blueprint para endpoints de autenticación de usuarios.

Incluye:
- /auth/login: Inicia sesión y devuelve un token.
- /auth/change_password: Permite a un usuario cambiar su contraseña.
"""

from flask import Blueprint, jsonify, request
from modelos import Usuario, Paciente, ValidationError
from config import UserRoles
from utils import token_generator
from extensions import db
from typing import Optional

# Definición del blueprint
auth_bp: Blueprint = Blueprint("auth_bp", __name__)

@auth_bp.route("/auth/login", methods= ["POST"])
def login():
    """
    Endpoint de login.
    Valida el JSON recibido, verifica credenciales y genera un token.

    JSON esperado:
    {
        "username": "usuario",
        "password": "contraseña"
    }

    Respuestas:
        200: Login exitoso, devuelve token y expiración.
        400: JSON inválido o schema incorrecto.
        401: Credenciales incorrectas o usuario inactivo.
    """

    data: Optional[dict[str,str]] = request.get_json(silent= True)
    if not data:
        return jsonify({"error": "JSON invalido o faltante"}), 400
    
    try:
        # Validación de esquema de login
        Usuario.check_schema(data, login= True)
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    
    # Buscar usuario en la base de datos
    usuario: Optional[Usuario] = db.session.query(Usuario).filter_by(username= data["username"]).first()
    if usuario:
        # Verificar contraseña
        if data["password"] == usuario.password:
            # Validación para pacientes. Si el paciente esta inactivo no se le permite logearse
            if usuario.rol == UserRoles.PACIENTE:
                paciente: Paciente = db.session.query(Paciente).filter_by(id_usuario= usuario.id_usuario).first()
                if paciente.estado == 'inactivo':
                    return jsonify({"error": "Credenciales incorrectas"}), 401
            
            # Generación del token y expiración
            token, expiration = token_generator(usuario.id_usuario, usuario.rol)
            return jsonify({"token": token, "expiration": expiration.isoformat()+ "Z"})
        else:
            return jsonify({"error": "Credenciales incorrectas"}), 401
    else:
        return jsonify({"error": "El usuario no existe"}), 401

@auth_bp.route("/auth/change_password", methods= ["PUT"])
def change_password():
    """
    Endpoint para cambiar la contraseña de un usuario.

    JSON esperado:
    {
        "username": "usuario",
        "password": "contraseña_actual",
        "new_password": "nueva_contraseña"
    }

    Respuestas:
        200: Contraseña cambiada correctamente.
        400: JSON inválido o schema incorrecto.
        404: Usuario no encontrado.
    """

    data: Optional[dict[str,str]] = request.get_json(silent= True)
    if not data:
        return jsonify({"error": "JSON invalido o faltante"}), 400
    
    try:
        # Validación de esquema de cambio de contraseña
        Usuario.check_schema(data, password_change= True)
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    
    # Buscar usuario en la base de datos
    usuario: Optional[Usuario] = db.session.query(Usuario).filter_by(username= data["username"]).first()
    if usuario:
        # Verificar contraseña actual
        if data["password"] == usuario.password:
            # Si es correcto, se cambia la contraseña
            usuario.password = data["new_password"]
            db.session.commit()
        return jsonify({"message": "Contraseña cambiada"})
    else:
        return jsonify({"error": "El usuario no existe"}), 404