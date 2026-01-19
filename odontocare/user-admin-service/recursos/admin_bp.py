"""
Blueprint para endpoints administrativos.
Incluye operaciones CRUD para el modelo Usuario,
Doctor, Paciente y Centro.
Todos los endpoints están protegidos mediante el decorador
required_authorization, permitiendo solo roles de administrador o 
peticiones provenientes desde servicios internos.
"""

from flask import Blueprint, jsonify, request
from modelos import Usuario, Doctor, Paciente, Centro, ValidationError
from config import UserRoles
from utils import required_authorization, random_password
from extensions import db
from sqlalchemy.exc import IntegrityError
from typing import Optional


# Definición del blueprint
admin_bp: Blueprint = Blueprint("admin_bp", __name__)

#------------------------------------------------------
# Operaciones CRUD para el modelo Usuario
#------------------------------------------------------
@admin_bp.route("/admin/usuarios", methods= ["GET"])
@required_authorization(rol_requerido= [UserRoles.ADMIN])
def get_all_users():
    """
    Obtiene todos los usuarios de la base de datos.
    Retorna una lista de diccionarios representando cada usuario.

    Retorno:
        200: Lista de usuarios
    """
    return jsonify([user.to_dict() for user in Usuario.query.all()])

@admin_bp.route("/admin/usuario/<int:id>", methods= ["GET"])
@required_authorization(rol_requerido= [UserRoles.ADMIN])
def get_user(id: int):
    """
    Obtiene un usuario específico por su ID.

    Args:
        id (int): ID del usuario

    Retorno:
        200: Usuario encontrado
        404: Usuario no encontrado
    """
    user: Usuario = Usuario.query.get_or_404(id)
    return jsonify(user.to_dict())

@admin_bp.route("/admin/usuario", methods=["POST"])
@required_authorization(rol_requerido= [UserRoles.ADMIN])
def create_user():
    """
    Crea un nuevo usuario.

    JSON esperado:
    {
        "username": "usuario",
        "password": "contraseña",
        "rol": "rol_usuario"
    }

    Retorno:
        201: Usuario creado exitosamente
        400: JSON inválido o schema incorrecto
        500: Usuario ya existe
    """
    data: Optional[dict[str,str]] = request.get_json(silent= True)
    if not data:
        return jsonify({"error": "JSON invalido o faltante"}), 400
    
    try:
        # Validación de esquema de usuario
        Usuario.check_schema(data)
    except ValidationError as e:
        return jsonify({"error": f"{e}. El usuario debe contener los campos username, password y rol"}), 400
    
    # Creación del usuario
    try:
        new_user: Usuario = Usuario(
                        username= data["username"],
                        password = data["password"],
                        rol = data["rol"]
                        )
        db.session.add(new_user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": f"El usuario {data['username']} ya existe"}), 500
    
    return jsonify(new_user.to_dict()), 201

@admin_bp.route("/admin/usuarios", methods=["POST"])
@required_authorization(rol_requerido= [UserRoles.ADMIN])
def create_users():
    """
    Crea múltiples usuarios en un solo request.

    JSON esperado: Lista de usuarios con los campos:
    [
        {"username": "...", "password": "...", "rol": "..."},
        ...
    ]

    Retornos:
        201: Usuarios creados con éxito
        400: JSON inválido o schema incorrecto
        500: Algún usuario ya existe
    """
    data: Optional[list[dict[str,str]]] = request.get_json(silent= True)
    if not data:
        return jsonify({"error": "JSON invalido o faltante"}), 400
    
    try:
        # Validación de cada usuario en el payload
        for user in data:
            Usuario.check_schema(user)
    except ValidationError as e:
        return jsonify({"error": f"{e}. El usuario debe contener los campos username, password y rol"}), 400  #Bad Request, el formato de usuario es incorrecto
    
    # Creación de usuarios
    try:
        new_users: list[Usuario] = [Usuario(username= user["username"],
                        password = user["password"],
                        rol = user["rol"]) for user in data]
        db.session.add_all(new_users)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        # Indica que usuario ya existe
        return jsonify({"error": f"El usuario {e.params[0]} ya existe"}), 500
    
    return jsonify({"message": "Usuarios creados con exito"}), 201

@admin_bp.route("/admin/usuario/<int:id>", methods= ["DELETE"])
@required_authorization(rol_requerido= [UserRoles.ADMIN])
def delete_user(id: int):
    """
    Elimina un usuario específico por su ID.

    Args:
        id (int): ID del usuario a eliminar.

    Retorno:
        200: Usuario eliminado exitosamente
        404: Usuario no encontrado
    """
    user: Usuario = Usuario.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "Usuario eliminado"})

#------------------------------------------------------
# Operaciones CRUD para el modelo Doctor
#------------------------------------------------------
@admin_bp.route("/admin/doctores", methods= ["GET"])
@required_authorization(rol_requerido= [UserRoles.ADMIN])
def get_all_doctors():
    """
    Obtiene todos los doctores registrados.

    Retorno:
        200: Lista de doctores en formato diccionario
    """
    return jsonify([doctor.to_dict() for doctor in Doctor.query.all()])

@admin_bp.route("/admin/doctor/<int:id>", methods= ["GET"])
@required_authorization(rol_requerido= [UserRoles.ADMIN, UserRoles.SERVICE],
                        return_payload= True)
def get_doctor(id: int, rol_usuario: str, rol_query: str):
    """
    Obtiene un doctor específico por su ID.
    Si el servicio de citas accede con una peticion de un 
    usuario con rol doctor la busqueda se hace a traves del
    id_usuario. Si se accede desde otros roles la busqueda
    se hace a traves del id_doctor

    Args:
        id (int): ID del doctor
        rol_usuario (str): Rol del usuario que hace la petición (inyectado por el decorador)
        rol_query (dict): Rol del usuario que hace la peticion a traves del servicio citas.
        Solo cuando se hacen peticiones desde el servicio citas

    Retorno:
        200: Doctor encontrado
        404: Doctor no encontrado
    """

    # Acceso especial desde servicio citas y con rol de usuario médico
    if rol_usuario == UserRoles.SERVICE and rol_query == UserRoles.MEDICO:
        doctor: Doctor = Doctor.query.filter_by(id_usuario= id).first()
    
    # Resto de petiones
    else:    
        doctor: Optional[Doctor] = Doctor.query.get_or_404(id)
    return jsonify(doctor.to_dict())

@admin_bp.route("/admin/doctor", methods=["POST"])
@required_authorization(rol_requerido= [UserRoles.ADMIN])
def create_doctor():
    """
    Crea un nuevo doctor y su usuario asociado automáticamente.
    Genera un username a partir del nombre y apellido y una contraseña aleatoria.

    JSON esperado:
    {
        "nombre": "Nombre",
        "apellido": "Apellido",
        "especialidad": "Especialidad"
    }

    Retorno:
        201: Doctor y usuario creados
        400: JSON inválido o schema incorrecto
        500: Usuario ya existe
    """
    data: Optional[dict[str,str]] = request.get_json(silent= True)
    if not data:
        return jsonify({"error": "JSON invalido o faltante"}), 400
    
    try:
        # Validación de esquema de doctor
        Doctor.check_schema(data)
    except ValidationError as e:
        return jsonify({"error": f"{e}. El doctor debe contener los campos nombre, apellido y especialidad"}), 400
    
    # Generación de nombres de usuario y contraseña
    username: str = ".".join((data["nombre"].strip(" ").lower(), data["apellido"].strip(" ").lower()))
    password: str = random_password()

    # Creación del usuario
    try:
        new_user: Usuario = Usuario(username= username, password= password, rol= UserRoles.MEDICO)
        db.session.add(new_user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": f"El usuario {username} ya existe"}), 500
    
    # Se recupera el id_usuario del usuario creado para la creación del doctor
    user_id = new_user.id_usuario

    # Creación del doctor asociado al usuario
    doctor: Doctor = Doctor(id_usuario= user_id, nombre= data["nombre"], apellido= data["apellido"], especialidad= data["especialidad"])
    db.session.add(doctor)
    db.session.commit()
    return jsonify({"doctor": doctor.to_dict(),
                    "user": new_user.to_dict()}), 201

@admin_bp.route("/admin/doctores", methods=["POST"])
@required_authorization(rol_requerido= [UserRoles.ADMIN])
def create_doctors():
    """
    Crea múltiples doctores y sus usuarios asociados en un solo request.

    JSON esperado: Lista de doctores
    [
        {"nombre": "...", "apellido": "...", "especialidad": "..."},
        ...
    ]

    Retorno:
        201: Doctores y usuarios creados
        400: JSON inválido o schema incorrecto
        500: Algún usuario ya existe
    """
    data: Optional[list[dict[str,str]]] = request.get_json(silent= True)
    if not data:
        return jsonify({"error": "JSON invalido o faltante"}), 400
    
    try:
        # Validación de esquema de doctor para cada doctor
        for doctor in data:
            Doctor.check_schema(doctor)
    except ValidationError as e:
        return jsonify({"error": f"{e}. El doctor debe contener los campos nombre, apellido y especialidad"}), 400
    
    # Generación de nombres de usuario y contraseña. Creación de los usuarios
    new_users: list[Usuario] = []
    for doctor in data:
        username: str = ".".join((doctor["nombre"].strip(" ").lower(), doctor["apellido"].strip(" ").lower()))
        password: str = random_password()
        new_users.append(Usuario(username= username, password= password, rol= UserRoles.MEDICO))
    
    # Comprueba si existe algun usuario
    try:
        db.session.add_all(new_users)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": f"El usuario {e.params[0]} ya existe"}), 500
    
    # Se recupera el id_usuario de los usuarios para la creación de doctores
    user_ids: list[int] = [new_user.id_usuario for new_user in new_users]
    
    # Creación de doctores asociados a usuarios
    doctors: list[Doctor] = []
    for doctor, user_id in zip(data, user_ids):
        doctors.append(Doctor(id_usuario= user_id,
                              nombre= doctor["nombre"],
                              apellido= doctor["apellido"],
                              especialidad= doctor["especialidad"]
                            )
                        )
    db.session.add_all(doctors)
    db.session.commit()
    return jsonify({"message": "Doctores creados con exito"}), 201

@admin_bp.route("/admin/doctor/<int:id>", methods= ["PUT"])
@required_authorization(rol_requerido= [UserRoles.ADMIN])
def change_doctor(id: int):
    """
    Actualiza la especialidad de un doctor existente.

    JSON esperado:
    {
        "especialidad": "Nueva Especialidad"
    }

    Retorno:
        200: Especialidad actualizada
        400: JSON inválido o schema incorrecto
        404: Doctor no encontrado
    """
    data: Optional[dict[str,str]] = request.get_json(silent= True)
    if not data:
        return jsonify({"error": "JSON invalido o faltante"}), 400
    
    try:
        # Validación de esquema de doctor
        Doctor.check_schema(data, update= True)
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    
    # Busqueda del doctor
    doctor: Doctor = Doctor.query.get_or_404(id)

    # Actualizar la especialidad del doctor
    if doctor.especialidad != data["especialidad"]:
        doctor.especialidad = data["especialidad"]
    db.session.commit()
    return jsonify({"message": "Especialidad de doctor cambiada"})

@admin_bp.route("/admin/doctor/<int:id>", methods= ["DELETE"])
@required_authorization(rol_requerido= [UserRoles.ADMIN])
def delete_doctor(id: int):
    """
    Elimina un doctor y su usuario asociado si existe.

    Args:
        id (int): ID del doctor a eliminar

    Retorno:
        200: Doctor eliminado exitosamente
        404: Doctor no encontrado
    """
    doctor: Optional[Doctor] = Doctor.query.get_or_404(id)
    if doctor.id_usuario is not None:
        usuario: Optional[Usuario] = Usuario.query.get_or_404(doctor.id_usuario)
        db.session.delete(usuario)
    db.session.delete(doctor)
    db.session.commit()
    return jsonify({"message": "Doctor eliminado"})

#------------------------------------------------------
# Operaciones CRUD para el modelo Paciente
#------------------------------------------------------
@admin_bp.route("/admin/pacientes", methods= ["GET"])
@required_authorization(rol_requerido= [UserRoles.ADMIN])
def get_all_patients():
    """
    Obtiene todos los pacientes registrados.
    Permite filtrar por estado usando query param: ?estado=activo/inactivo

    Retorno:
        200: Lista de pacientes (vacía si no hay coincidencias)
    """
    estado: Optional[str] = request.args.get("estado")
    if estado:
        pacientes: list[Optional[Paciente]] = Paciente.query.filter_by(estado= estado)
    else:
        pacientes: list[Optional[Paciente]] = Paciente.query.all()
    if pacientes:
        return jsonify([patient.to_dict() for patient in pacientes])
    return jsonify([])

@admin_bp.route("/admin/paciente/<int:id>", methods= ["GET"])
@required_authorization(rol_requerido= [UserRoles.ADMIN, UserRoles.SERVICE],
                        return_payload= True)
def get_patient(id: int, rol_usuario: str, rol_query: str):
    """
    Obtiene un paciente específico por su ID.
    Si el servicio de citas accede con una peticion de un 
    usuario con rol paciente la busqueda se hace a traves del
    id_usuario. Si el servicio de citas accede con una peticion de un 
    usuario con rol admin filtra por estado y usa id_paciente
    Si se accede directamente desde rol admin se usa id_paciente
    para la busqueda

    Args:
        id (int): ID del paciente
        rol_usuario (str): Rol del usuario que hace la petición (inyectado por el decorador)
        rol_query (dict): Rol del usuario que hace la peticion a traves del servicio citas.
        Solo cuando se hacen peticiones desde el servicio citas

    Query params:
        estado (str, opcional): Filtra el paciente por su estado (activo/inactivo)

    Retorno:
        200: Paciente encontrado
        404: Paciente no encontrado
    """
    # Acceso especial desde servicio citas con rol de usuario paciente o admin
    if rol_usuario == UserRoles.SERVICE:
        if rol_query == UserRoles.PACIENTE:
            paciente: Paciente = Paciente.query.filter_by(id_usuario= id).first()

        elif rol_query == UserRoles.ADMIN:
            estado: Optional[str] = request.args.get('estado')
            if estado:
                paciente: Optional[Paciente] = Paciente.query.filter_by(id_paciente= id, estado= estado).first()
            else:
                paciente: Optional[Paciente] = Paciente.query.filter_by(id_paciente= id).first()
        if not paciente:
            return jsonify({}), 404
        
        return jsonify(paciente.to_dict())
    
    # Accediendo directamente con rol admin
    elif rol_usuario == UserRoles.ADMIN:
        estado: Optional[str] = request.args.get("estado")
        if estado:
            paciente: Optional[Paciente] = db.session.query(Paciente).filter_by(id_paciente= id, estado= estado).first()
        else:
            paciente: Optional[Paciente] = Paciente.query.get_or_404(id)
        if not paciente:
            return jsonify({}), 404
        
        return jsonify(paciente.to_dict())

@admin_bp.route("/admin/paciente", methods=["POST"])
@required_authorization(rol_requerido= [UserRoles.ADMIN])
def create_patient():
    """
    Crea un nuevo paciente y su usuario asociado automáticamente.
    Genera un username a partir del nombre y apellido
    y una contraseña aleatoria.

    JSON esperado:
    {
        "nombre": "Nombre",
        "apellido": "Apellido",
        "telefono": "Número de teléfono",
        "estado": "activo" | "inactivo"
    }

    Retorno:
        201: Paciente y usuario creados
        400: JSON inválido o schema incorrecto
        500: Usuario ya existe
    """
    data: Optional[dict[str,str]]= request.get_json(silent= True)
    if not data:
        return jsonify({"error": "JSON invalido o faltante"}), 400
    
    try:
        # Validación del esquema de paciente
        Paciente.check_schema(data)
    except ValidationError as e:
        return jsonify({"error": f"{e}. El paciente debe contener los campos nombre, apellido, telefono y estado"}), 400
    
    # Generación de nombres de usuario y contraseña.
    username: str = ".".join((data["nombre"].strip(" ").lower(), data["apellido"].strip(" ").lower()))
    password: str = random_password()

    # Creación del usuario
    try:
        new_user: Usuario = Usuario(username= username, password= password, rol= UserRoles.PACIENTE)
        db.session.add(new_user)
        db.session.commit()
    except IntegrityError:
        return jsonify({"error": f"El usuario {username} ya existe"}), 500
    # Se recupera el id_usuario del usuario creado para la creación del paciente
    user_id: int = new_user.id_usuario

    # Creación del paciente asociado al usuario
    paciente: Paciente = Paciente(id_usuario= user_id,
                      nombre= data["nombre"],
                      apellido= data["apellido"],
                      telefono= data["telefono"],
                      estado= data["estado"]
                      )
    db.session.add(paciente)
    db.session.commit()
    return jsonify({"paciente": paciente.to_dict(),
                    "user": new_user.to_dict()}), 201

@admin_bp.route("/admin/pacientes", methods=["POST"])
@required_authorization(rol_requerido= [UserRoles.ADMIN])
def create_patients():
    """
    Crea múltiples pacientes y sus usuarios asociados en un solo request.

    JSON esperado: Lista de pacientes
    [
        {"nombre": "...", "apellido": "...", "telefono": "...", "estado": "..."},
        ...
    ]

    Retorno:
        201: Pacientes y usuarios creados exitosamente
        400: JSON inválido o schema incorrecto
        500: Algún usuario ya existe
    """
    data: Optional[dict[str,str]] = request.get_json(silent= True)
    if not data:
        return jsonify({"error": "JSON invalido o faltante"}), 400
    try:
        # Validación de esquema de paciente para cada paciente
        for paciente in data:
            Paciente.check_schema(paciente)
    except ValidationError as e:
        return jsonify({"error": f"{e}. El paciente debe contener los campos nombre, apellido, telefono y estado"}), 400
    
    # Generación de nombres de usuario y contraseña. Creación de los usuarios
    new_users: list[Usuario] = []
    for paciente in data:
        username: str = ".".join((paciente["nombre"].strip(" ").lower(), paciente["apellido"].strip(" ").lower()))
        password: str = random_password()
        new_users.append(Usuario(username= username, password= password, rol= UserRoles.PACIENTE))
    
    # Comprueba si existe algun usuario
    try:
        db.session.add_all(new_users)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": f"El usuario {e.params[0]} ya existe"}), 500
    
    # Se recupera el id_usuario de los usuarios para la creación de pacientes
    user_ids: list[int] = [new_user.id_usuario for new_user in new_users]
    
    # Creación de doctores asociados a usuarios
    pacientes: list[Doctor] = []
    for paciente, user_id in zip(data, user_ids):
        pacientes.append(Paciente(id_usuario= user_id,
                                  nombre= paciente["nombre"],
                                  apellido= paciente["apellido"],
                                  telefono= paciente["telefono"],
                                  estado= paciente["estado"]
                                )
                            )
    db.session.add_all(pacientes)
    db.session.commit()
    return jsonify({"message": "Pacientes creados con exito"}), 201

@admin_bp.route("/admin/paciente/<int:id>", methods= ["PUT"])
@required_authorization(rol_requerido= [UserRoles.ADMIN])
def change_patient(id: int):
    """
    Actualiza los datos de un paciente existente (teléfono y estado).

    JSON esperado:
    {
        "telefono": "Número de teléfono",
        "estado": "activo" | "inactivo"
    }

    Args:
        id (int): ID del paciente a actualizar

    Retorno:
        200: Datos del paciente actualizados
        400: JSON inválido o schema incorrecto
        404: Paciente no encontrado
    """
    data: Optional[dict[str,str]] = request.get_json(silent= True)
    if not data:
        return jsonify({"error": "JSON invalido o faltante"}), 400
    
    try:
        # Validación de esquema de paciente
        Paciente.check_schema(data, update= True)
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    
    # Busqueda del paciente 
    paciente: Optional[Paciente] = Paciente.query.get_or_404(id)

    # Actualizar la especialidad del doctor
    if paciente.telefono != data["telefono"]:
        paciente.telefono = data["telefono"]
    if paciente.estado != data["estado"]:
        paciente.estado = data["estado"]
    db.session.commit()
    return jsonify({"message": "Datos del paciente actualizados"})

@admin_bp.route("/admin/paciente/<int:id>", methods= ["DELETE"])
@required_authorization(rol_requerido= [UserRoles.ADMIN])
def delete_patient(id: int):
    """
    Elimina un paciente y su usuario asociado si existe.

    Args:
        id (int): ID del paciente a eliminar

    Retorno:
        200: Paciente eliminado exitosamente
        404: Paciente no encontrado
    """
    paciente: Optional[Paciente] = Paciente.query.get_or_404(id)
    if paciente.id_usuario is not None:
        usuario: Optional[Usuario] = Usuario.query.get_or_404(paciente.id_usuario)
        db.session.delete(usuario)
    db.session.delete(paciente)
    db.session.commit()
    return jsonify({"message": "Paciente eliminado"})

#------------------------------------------------------
# Operaciones CRUD para el modelo Centro
#------------------------------------------------------
@admin_bp.route("/admin/centros", methods= ["GET"])
@required_authorization(rol_requerido= [UserRoles.ADMIN])
def get_clinics():
    """
    Obtiene todos los centros registrados.

    Retorno:
        200: Lista de centros en formato diccionario
    """
    return jsonify([clinic.to_dict() for clinic in Centro.query.all()])

@admin_bp.route("/admin/centro/<int:id>", methods= ["GET"])
@required_authorization(rol_requerido= [UserRoles.ADMIN, UserRoles.SERVICE])
def get_clinic(id: int):
    """
    Obtiene un centro específico por su ID.

    Args:
        id (int): ID del centro

    Retorno:
        200: Centro encontrado
        404: Centro no encontrado
    """
    clinic: Optional[Centro] = Centro.query.get_or_404(id)
    return jsonify(clinic.to_dict())

@admin_bp.route("/admin/centro", methods=["POST"])
@required_authorization(rol_requerido= [UserRoles.ADMIN])
def create_clinic():
    """
    Crea un nuevo centro.

    JSON esperado:
    {
        "nombre": "Nombre del centro",
        "direccion": "Dirección del centro"
    }

    Retorno:
        201: Centro creado exitosamente
        400: JSON inválido o schema incorrecto
    """
    data: Optional[dict[str,str]] = request.get_json(silent= True)
    if not data:
        return jsonify({"error": "JSON invalido o faltante"}), 400
    
    try:
        # Validación de esquema de centro
        Centro.check_schema(data)
    except ValidationError as e:
        return jsonify({"error": f"{e}. El centro debe contener los campos nombre y dirección"}), 400
    
    # Creación del centro
    centro: Centro = Centro(nombre= data["nombre"], direccion= data["direccion"])
    db.session.add(centro)
    db.session.commit()
    return jsonify(centro.to_dict()), 201

@admin_bp.route("/admin/centros", methods=["POST"])
@required_authorization(rol_requerido= [UserRoles.ADMIN])
def create_clinics():
    """
    Crea múltiples centros en un solo request.

    JSON esperado: Lista de centros
    [
        {"nombre": "...", "direccion": "..."},
        ...
    ]

    Retorno:
        201: Centros creados exitosamente
        400: JSON inválido o schema incorrecto
    """
    data: Optional[dict[str,str]] = request.get_json(silent= True)
    if not data:
        return jsonify({"error": "JSON invalido o faltante"}), 400
    
    try:
        # Validación del esquema de centro
        for centro in data:
            Centro.check_schema(centro)
    except ValidationError as e:
        return jsonify({"error": f"{e}. El centro debe contener los campos nombre y dirección"}), 400
    
    # Creación de los centros
    centros: list[Centro] = [Centro(nombre= centro["nombre"], direccion= centro["direccion"]) for centro in data]
    db.session.add_all(centros)
    db.session.commit()
    return jsonify({"message": "Centros creados con exito"}), 201

@admin_bp.route("/admin/centro/<int:id>", methods=["PUT"])
@required_authorization(rol_requerido= [UserRoles.ADMIN])
def update_clinic(id: int):
    """
    Actualiza los datos de un centro existente.

    JSON esperado:
    {
        "nombre": "Nuevo nombre",
        "direccion": "Nueva dirección"
    }

    Args:
        id (int): ID del centro a actualizar

    Retorno:
        200: Datos del centro actualizados
        400: JSON inválido o schema incorrecto
        404: Centro no encontrado
    """
    data: Optional[dict[str,str]] = request.get_json(silent= True)
    if not data:
        return jsonify({"error": "JSON invalido o faltante"}), 400
    
    try:
        # Validación de esquema de centro
        Centro.check_schema(data)
    except ValidationError as e:
        return jsonify({"error": f"{e}. El centro debe contener los campos nombre y dirección"}), 400
    
    # Busqueda del centro
    centro: Optional[Centro] = Centro.query.get_or_404(id)

    # Actualizar los datos del centro
    if centro.nombre != data["nombre"]:
        centro.nombre = data["nombre"]
    if centro.direccion != data["direccion"]:
        centro.direccion = data["direccion"]
    db.session.commit()
    return jsonify({"message": "Datos del centro actualizados"})

@admin_bp.route("/admin/centro/<int:id>", methods= ["DELETE"])
@required_authorization(rol_requerido= [UserRoles.ADMIN])
def delete_center(id: int):
    """
    Elimina un centro específico por su ID.

    Args:
        id (int): ID del centro a eliminar

    Retorno:
        200: Centro eliminado exitosamente
        404: Centro no encontrado (manejado por get_or_404)
    """
    centro: Optional[Centro] = Centro.query.get_or_404(id)
    db.session.delete(centro)
    db.session.commit()
    return jsonify({"message": "Centro eliminado"})