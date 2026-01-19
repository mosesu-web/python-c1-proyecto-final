"""
Blueprint que gestiona la creación, consulta y cancelación de citas médicas.
Incluye validaciones por rol de usuario, control de disponibilidad y verificación
de existencia de doctor, paciente y centro médico mediante servicios externos.
"""

from flask import Blueprint, jsonify, request
from modelos import Cita, ValidationError
from config import UserRoles
from utils import required_authorization
from extensions import db
from datetime import datetime, timedelta
from typing import Optional, Any
from utils.api_client import get_patient, get_doctor, get_clinic

# Definición del blueprint
citas_bp = Blueprint("citas_bp", __name__)

@citas_bp.route("/citas", methods= ["POST"])
@required_authorization(rol_requerido=[UserRoles.ADMIN, UserRoles.PACIENTE],
                        return_payload= True)
def create_appointment(rol_usuario: str, user_id: int):
    """
    Crea una nueva cita médica.

    La cita se valida según el rol del usuario:
    - El paciente solo puede crear citas para sí mismo con estado "Pendiente".
    - El administrador puede crear citas para cualquier paciente y definir el estado.

    Retorno:
        201: Cita creada exitosamente
        400: JSON inválido, datos faltantes o cita duplicada
        404: Doctor, centro o paciente inexistente o inactivo
    """

    data: Optional[dict[str,str|int]] = request.get_json(silent= True)
    if not data:
        return jsonify({"error": "JSON invalido o faltante"}), 400
    
    try:
        # Validación del esquema según el rol
        Cita.check_schema(data, rol= rol_usuario)
    except ValidationError as e:
        return jsonify({"error": f"{e}. Faltan campos o son errones"}), 400
    
    # Lógica específica según rol
    if rol_usuario == UserRoles.PACIENTE:
        id_paciente: int = user_id
        estado: str = "Pendiente"

        # Validación de datos a traves de servicio user-admin
        doctor = get_doctor(data["id_doctor"], rol_usuario)
        centro = get_clinic(data["id_centro"])
        paciente = get_patient(user_id, rol_usuario)
    else:
        id_paciente: int = data["id_paciente"]
        estado: str = data["estado"]

        # Validación de datos a traves de servicio user-admin
        doctor: Optional[dict[Any,Any]] = get_doctor(data["id_doctor"], rol_usuario)
        centro: Optional[dict[Any,Any]] = get_clinic(data["id_centro"])
        paciente: Optional[dict[Any,Any]] = get_patient(data["id_paciente"], rol_usuario)
    
    # Verificación de existencia y estado activo del paciente
    if (not doctor or
            not centro or
            not paciente or paciente.get("estado") == "inactivo"):
            return jsonify({"error": "El doctor, centro o paciente no existe o esta inactivo"}), 404

    # Verificación de disponibilidad (misma fecha, doctor y centro)
    hay_citas: Optional[Cita] = Cita.query.filter_by(id_doctor= data["id_doctor"],
                                           id_centro= data["id_centro"],
                                           fecha= datetime.fromisoformat(data["fecha"])
                                           ).first()
    
    # Si no hay cita o la anterior fue cancelada, se permite crearla
    if not hay_citas or hay_citas.estado == "Cancelada":
        cita: Cita = Cita(fecha= datetime.fromisoformat(data["fecha"].replace("Z", "+00:00")),
                    motivo= data["motivo"],
                    estado= estado,
                    id_paciente= id_paciente,
                    id_doctor= data["id_doctor"],
                    id_centro= data["id_centro"],
                    id_usuario_registra= user_id
                    )
        db.session.add(cita)
        db.session.commit()
        return jsonify(cita.to_dict()), 201
    
    # Si ya hay una cita para ese centro con el doctor y fecha elegido, se devuelve un mensaje
    else:
        return jsonify(
            {
                "message": (f"Ya hay una cita asignada para el Dr. {doctor.get('apellido')}"
                            f"en el centro {centro.get('nombre')} para el dia {data['fecha'].split('T')[0]} "
                            f"a las {data['fecha'].split('T')[1].rsplit(':',1)[0]} horas")
            }
            ),400

@citas_bp.route("/citas", methods= ["GET"])
@required_authorization(rol_requerido=[UserRoles.ADMIN, UserRoles.MEDICO, UserRoles.SECRETARIA],
                        return_payload= True)
def get_appointments(rol_usuario: str, user_id: int):
    """
    Obtiene citas médicas según el rol del usuario y los filtros enviados.

    - ADMIN: puede filtrar por paciente, doctor, centro, estado y fecha.
    - SECRETARIA: puede consultar citas por fecha.
    - MEDICO: obtiene únicamente sus propias citas.

    Retorno:
        200: Lista de citas
        400: Filtros inválidos o faltantes
    """

    # Para roles distintos a doctor se necesita un JSON
    if not rol_usuario == UserRoles.MEDICO:
        data: Optional[dict[str,str|int]] = request.get_json(silent= True)
        if not data:
            return jsonify({"error": "JSON invalido o faltante"}), 400
        
        try:
            # Validación del esquema según el rol
            Cita.check_schema(data, rol_usuario, query= True)
        except ValidationError as e:
            return jsonify({"error": f"{e}. Faltan campos o son erroneos"}), 400
    
    # Consultas según rol
    # Rol admin
    if rol_usuario == UserRoles.ADMIN:
        # Diccionario dínamico para la consulta
        query: dict[str,str|int] = {"id_paciente": data.get("id_paciente"),
                 "id_doctor": data.get("id_doctor"),
                 "id_centro": data.get("id_centro"),
                 "estado": data.get("estado")
                 }
        query = {k:v for k,v in query.items() if v is not None}  # Se eliminan los campos faltantes

        inicio: datetime|None = None
        fin: datetime|None = None

        # Si hay fecha en la consulta, se define el inicio y el fin del filtrado
        if data.get("fecha"):
            inicio =  datetime.fromisoformat(data.get("fecha"))
            fin = inicio + timedelta(days= 1)

        # Consulta si hay parametros de consulta pero no fecha
        if query and not inicio and not fin:
            citas: Optional[list[Cita]] = Cita.query.filter_by(**query).order_by(Cita.fecha.asc()).all()
        
        # Consulta si hay parametros de consulta y fecha
        elif query and inicio and fin:
            citas: Optional[list[Cita]] = Cita.query.filter(Cita.fecha.between(inicio, fin)).filter_by(**query).order_by(Cita.fecha.asc()).all()
        
        # Consulta si hay fecha
        elif inicio and fin:
            citas: Optional[list[Cita]] = Cita.query.filter(Cita.fecha.between(inicio, fin)).order_by(Cita.fecha.asc()).all()
        
        # Devuelve un mensaje de error si no hay parametros de consulta
        else:
            return jsonify({"error": "Se necesita al menos un parametro de filtrado"}), 400
    
    # Rol secretaria
    elif rol_usuario == UserRoles.SECRETARIA:
        # Solo filtra por fechas
        inicio: datetime =  datetime.fromisoformat(data.get("fecha"))
        fin: datetime = inicio + timedelta(days= 1)
        
        # si hay fecha en los parámetros de consulta se ejecuta
        if inicio and fin:
            citas: Optional[list[Cita]] = Cita.query.filter(Cita.fecha.between(inicio, fin)).order_by(Cita.fecha.asc()).all()
        else:
            return jsonify({"error": "Se necesita al menos un parametro de filtrado"}), 400
    
    # Rol doctor
    elif rol_usuario == UserRoles.MEDICO:
        # Se usa el id_usuario contenido en el token para identificar al usuario 
        query = {"id_doctor": get_doctor(user_id, rol_usuario).get("id_doctor")}
        query = {k:v for k,v in query.items() if v is not None}
        
        if query:
            # Solo filtra las citas asignadas a él mismo
            citas: Optional[list[Cita]] = Cita.query.filter_by(**query).order_by(Cita.fecha.asc()).all()
        else:
            return jsonify({"error": "Se necesita al menos un parametro de filtrado"}), 400
    
    # Tras realizar la consulta, si esta contiene citas, se retornan
    if citas:
        return jsonify([cita.to_dict() for cita in citas])
    else:
        return jsonify({})

@citas_bp.route("/citas/<int:id>", methods= ["PUT"])
@required_authorization(rol_requerido=[UserRoles.ADMIN, UserRoles.SECRETARIA])
def cancel_appointment(id: int):
    """
    Cancela una cita médica existente.

    Solo los usuarios con rol ADMIN o SECRETARIA pueden cancelar citas.
    Si la cita ya se encuentra cancelada, se informa al usuario.

    Retorno:
        200: Cita cancelada o ya cancelada
        404: Cita no encontrada
    """
    cita: Optional[Cita] = Cita.query.get_or_404(id)

    if cita.estado != "Cancelada":
        cita.estado = "Cancelada"
        db.session.commit()
        return jsonify({"message": "Cita cancelada"})
    
    return jsonify({"message": "La cita ya estaba cancelada"})




