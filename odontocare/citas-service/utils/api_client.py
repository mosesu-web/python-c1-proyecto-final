"""
Cliente HTTP para interactuar con el servicio de user-admin.
Este módulo encapsula las llamadas a la API externa para obtener información
de doctores, clínicas y pacientes, manejando autenticación mediante tokens.
"""

import requests
from requests.exceptions import HTTPError
from typing import Any
from utils import ServiceTokenManager
from config import Config

# Gestor de tokens de servicio.
# Delta indica el margen en segundos para la renovación del token antes de que caduque
token_manager: ServiceTokenManager = ServiceTokenManager(delta= 120)


def get_doctor(id: int, user_rol: str) -> dict[Any, Any]:
    """
    Obtiene la información de un doctor por su ID.

    Args:
        id (int): ID del doctor.
        user_rol (str): Rol del usuario utilizado para solicitar el token
                        de autenticación.

    Returns:
        dict: Información del doctor en formato JSON.
              Retorna un diccionario vacío si ocurre un error HTTP.
    """
    
    # URL del servicio de user-admin
    url: str = f"{Config.USER_ADMIN_SERVICE_URL}/api/v1/admin/doctor/{id}"

    # Obtención del token según el rol del usuario
    token: str = token_manager.get_token(user_rol)

    # Cabeceras HTTP con autorización
    headers: dict[str,str] = {"Content-type": "application/json", 
                              "Authorization": f"Bearer {token}"}
    
    # Petición GET
    response = requests.get(url= url, headers= headers)

    try:
        # Lanza una excepción si el status code es 4xx o 5xx
        response.raise_for_status()
    except HTTPError:
        # Si se produjo un error o no existe el item devuelve un dict vacio
        return {}
    
    # Devuelve el contenido de la respuesta en formato JSON
    return response.json()

def get_clinic(id: int) -> dict[Any, Any]:
    """
    Obtiene la información de un centro por su ID.

    Args:
        id (int): ID del centro.

    Returns:
        dict: Información de la clínica en formato JSON.
              Retorna un diccionario vacío si ocurre un error HTTP.
    """
    # URL del servicio de user-admin
    url = f"{Config.USER_ADMIN_SERVICE_URL}/api/v1/admin/centro/{id}"
    
    # Obtención del token
    token = token_manager.get_token()

    # Cabeceras HTTP con autorización
    headers = {"Content-type": "application/json", 
               "Authorization": f"Bearer {token}"}
    
    # Petición GET
    response = requests.get(url= url, headers= headers)
    try:
        # Lanza una excepción si el status code es 4xx o 5xx
        response.raise_for_status()
    except HTTPError:
        # Si se produjo un error o no existe el item devuelve un dict vacio
        return {}
    
    # Devuelve el contenido de la respuesta en formato JSON
    return response.json()

def get_patient(id: int, user_rol: str) -> dict[str,Any]:
    """
    Obtiene la información de un paciente activo por su ID.

    Args:
        id (int): ID del paciente.
        user_rol (str): Rol del usuario utilizado para solicitar el token
                        de autenticación.

    Returns:
        dict: Información del paciente en formato JSON.
              Retorna un diccionario vacío si ocurre un error HTTP
    """
    # URL del servicio de user-admin con filtro de pacientes activos
    url = f"{Config.USER_ADMIN_SERVICE_URL}/api/v1/admin/paciente/{id}?estado=activo"
    
    # Obtención del token
    token = token_manager.get_token(user_rol)

    # Cabeceras HTTP con autorización
    headers = {"Content-type": "application/json", 
               "Authorization": f"Bearer {token}"}
    
    # Petición GET
    response = requests.get(url= url, headers= headers)
    try:
        # Lanza una excepción si el status code es 4xx o 5xx
        response.raise_for_status()
    except HTTPError:
        # Si se produjo un error o no existe el item devuelve un dict vacio
        return {}
    
    # Devuelve el contenido de la respuesta en formato JSON
    return response.json()

