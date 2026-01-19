"""
Decorador para restringir el acceso a rutas que requieran autorización.
Restringe el acceso en función del rol del usuario. Opcionalmente, pasa
parámetros decodificados del payload del token.
"""

from functools import wraps
from flask import jsonify, request
from .jwt_utils import token_decoder
from datetime import datetime
from typing import Callable, Any


def required_authorization(rol_requerido: list[str],
                           return_payload: bool= False) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorador para proteger endpoints verificando rol de usuario mediante token.

    Puede recibir tokens de usuarios o del servicio de citas. Si es un token del
    servicio citas, este contendrá además del rol requerido para acceder al endpoint
    el rol del usuario que hace la petición al servicio de citas.
    Esto sirve para agilizar las petiones del servicio citas a los endpoints:

    GET /admin/doctor/id con rol usuario doctor.
    GET /admin/paciente/id con el rol usuario paciente.
    
    En esta petición el parámetro id hace referencia al id_usuario del doctor o
    paciente. De esta manera, se ahorra una consulta para averiguar el id_doctor
    o id_paciente a partir del id_usuario que contiene el token de login.    

    Args:
        rol_requerido (list[str]): Lista de roles permitidos para acceder al endpoint.
        return_payload (bool): Si es True, pasa parámetros del payload decodificado al endpoint.

    Example:
        @app.route("/admin/doctores", methods= ['GET'])
        @required_authorization(["admin"])
        def get_doctors():
            return "Doctor"

    Returns:
        Función decorada que valida la autorización antes de ejecutar el endpoint.
    """
    def internal_decorator(f: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Obtiene el token del header Authorization
            auth_header: str | None = request.headers.get("Authorization")
            if not auth_header:
                return jsonify({"error": "Token no proporcionado"}), 401
            
            try:
                # Comprobar que el formato sea Bearer token
                auth_type, token = auth_header.split(" ")
                if auth_type.lower() != "bearer":
                    return jsonify({"error": "Formato de autorización incorrecto"}), 401
                
                # Decodificar el token
                payload: dict[str, str|int|datetime] = token_decoder(token)
                rol_usuario: str = payload["role"]
                
                # Opcional, solo contiene valores cuando se hace la peticion interna
                rol_query: str|None = payload.get("user_role")

                # Verificar si el usuario tiene acceso al endpoint
                if rol_usuario not in rol_requerido:
                    return jsonify({"message": "Permiso denegado"}), 403
            
            except Exception as e:
                # Errores de decodificacion o formato del token
                return jsonify({ "error": str(e)})
            
            # Si return_payload es True devuelve al endpoint parámetros del payload
            if return_payload:
                # rol_usuario: rol del usuario que hace la petición al endpoint
                # rol_query: para peticiones internas del servicio citas. Contiene el
                # rol del usuario que hace la petición al servicio citas.
                return f(*args, **kwargs, rol_usuario= rol_usuario, rol_query= rol_query)
            return f(*args, **kwargs)
        return wrapper
    return internal_decorator