"""
Módulo de utilidades para carga de datos y creación de citas médicas.

Incluye:
- Manejo de URLs de servicios.
- Lectura y carga de archivos CSV a la base de datos.
- Login en el sistema con usuario y contraseña.
- Carga inicial de datos de usuarios, doctores, pacientes y centros.
- Creación interactiva de citas médicas con selección de centro, doctor, paciente y hora disponible.

Funciones principales:
- login(): Autentica a un usuario y retorna un token.
- read_load_data(token): Carga los datos iniciales usando el token de autenticación.
- create_appointment(token): Interactúa con el usuario para crear una cita médica.
"""
import re
import json
from typing import Optional

import pwinput
import requests
from datetime import datetime
from requests import HTTPError


class AppUrls:
    """Contiene las URLs base de los servicios disponibles."""

    USER_ADMIN = "http://localhost:5001"
    CITAS = "http://localhost:5002"


class CSVDataHAndler:
    """Clase para leer archivos CSV y convertirlos a JSON."""

    def __init__(self):
        self.path: str = "example-data/datos.csv"
        self.json: dict[str,list[dict[str,str]]] = {}

    def read_csv(self):
        """
        Lee un archivo CSV y separa los datos por tablas según el marcador 'table_name'.

        Al finalizar, convierte los datos a un formato JSON y lo almacena.
        """
        tables: dict[str,list[str]] = {} 
        current_table:list[str] = []
        table_name: str = ""
        with open(self.path, "r", encoding= 'utf-8') as fr:
            for line in fr.readlines():
                line: str = line.strip()
                if "table_name" in line:
                    table_name = line.split(":")[1]
                    continue
                if not line:
                    tables[table_name]= current_table
                    table_name = ""
                    current_table = []
                else:
                    current_table.append(line)
            # Guardar la última tabla
            tables[table_name] = current_table
        self.json = self.to_json(tables)

    def to_json(self, tables: dict[str,list[str]]) -> dict[str,list[dict[str,str]]]:
        """
        Convierte la estructura de tablas CSV en un diccionario JSON.

        Args:
            tables (dict): Diccionario con listas de strings por tabla.

        Returns:
            dict: Diccionario con listas de diccionarios por tabla.
        """

        json_data: dict[str,list[dict[str,str]]]= {}
        for table_name, table in tables.items():
            keys: list[str] = [k for k in table[0].split(",")]
            values: list[list[str]] = [[v for v in row.split(",")] for row in table[1:]]
            table_data: list[dict[str, str]] = [{k:v for k,v in zip(keys, row)} for row in values]
            json_data[table_name] = table_data
        return json_data

def login() -> str|None:
    """
    Solicita usuario y contraseña, realiza login en el servicio user-admin y retorna un token.

    Returns:
        str | None: Token de autenticación si el login fue exitoso, None en caso de error.
    """

    user: str = input("Usuario: ")
    password: str = pwinput.pwinput(prompt="Contraseña: ", mask="*")
    
    # Cabecera y cuerpo de la solicitud
    body: dict[str, str] = {"username": user,
                            "password": password}
    headers: dict[str, str] = {"Content-type": "application/json"}
    json_body = json.dumps(body)
    url = f"{AppUrls.USER_ADMIN}/api/v1/auth/login"

    # Solicitud HTTP GET
    response = requests.post(url, headers= headers, data= json_body)
    try:
        response.raise_for_status()
    except HTTPError as e:
        print(f"{e.response.json().get('error')}")
        return None

    return response.json().get("token")

def read_load_data(token: str):
    """
    Carga datos iniciales (usuarios, doctores, pacientes y centros) al servicio user-admin usando el token.

    Args:
        token (str): Token para autorización.
    """

    def write_data(table_name: str, table: list[dict[str,str]], auth_token: str):
        """Envía los datos de cada tabla al endpoint correspondiente."""

        base_url: str = AppUrls.USER_ADMIN
        if table_name == 'usuarios':
            url: str = f"{base_url}/api/v1/admin/usuarios"
        elif table_name == 'doctores':
            url: str = f"{base_url}/api/v1/admin/doctores"
        elif table_name == 'pacientes':
            url: str = f"{base_url}/api/v1/admin/pacientes"
        elif table_name == 'centros':
            url: str = f"{base_url}/api/v1/admin/centros"
        else:
            raise Exception(f"La tabla {table_name} no es una tabla válida")
        
        # Cabeceras con autorización y cuerpo de la solicitud
        headers: dict[str,str] = {"Content-type": "application/json",
                                "Authorization": f"Bearer {auth_token}"}
        json_body = json.dumps(table)
        
        # Solicitud HTTP GET al endpoint correspondiente
        response = requests.post(url, headers= headers, data= json_body)
        try:
            response.raise_for_status()
        except HTTPError as e:
            print(f"Se produjo un error: {e.response.json().get('error')}")
        else:
            print(f"Datos de {table_name} volcados correctamente")

    csv = CSVDataHAndler()
    csv.read_csv()
    for table_name, table in csv.json.items():
        write_data(table_name, table, token)

def create_appointment(token: str) -> bool:
    """
    Interactúa con el usuario para crear una cita médica:
    1. Selecciona centro, doctor.
    2. Muestra horas disponibles.
    3. Selecciona paciente y recoge motivo de la cita.
    3. Envía la cita al servicio de citas.

    Args:
        token (str): Token JWT para autorización.

    Returns:
        (bool): Devuelve True si la cita se creo con exito
    """

    def get_data(table_name: str, auth_token: str) -> dict[str, str]:
        """
        Recupera datos de centros, doctores o pacientes y permite seleccionar uno.

        Esta función consulta el servicio user-admin según el tipo de tabla
        indicado en `table_name`, imprime las opciones disponibles y permite
        al usuario elegir una de ellas por índice.

        Args:
            table_name (str): Nombre de la tabla a consultar. Debe ser 'doctores',
                            'pacientes' o 'centros'.
            auth_token (str): Token válido para autorización.

        Returns:
            dict[str, str]: Diccionario con los datos del elemento seleccionado.

        Raises:
            Exception: Si `table_name` no es válido o tiene acceso restringido.
        """
        # Construcción de la URL y formato de presentación según la tabla
        base_url: str = AppUrls.USER_ADMIN
        if table_name == 'doctores':
            url: str = f"{base_url}/api/v1/admin/doctores"
            keys: list[str] = ["nombre", "apellido", "especialidad"]
            row_string: str = "- Doctor: {0} {1} especialista en {2}"
        elif table_name == 'pacientes':
            url: str = f"{base_url}/api/v1/admin/pacientes?estado=activo"
            keys: list[str] = ["nombre", "apellido"]
            row_string: str = "- Paciente: {0} {1}"
        elif table_name == 'centros':
            url: str = f"{base_url}/api/v1/admin/centros"
            keys: list[str] = ["nombre"]
            row_string: str = "- Centro: {0}"
        else:
            raise Exception(f"La tabla {table_name} tiene acceso restringido o no existe")
        
        # Cabeceras con autorización
        headers: dict[str,str] = {"Content-type": "application/json",
                                "Authorization": f"Bearer {auth_token}"}
        
        # Solicitud HTTP GET al endpoint correspondiente
        response = requests.get(url, headers= headers)
        try:
            response.raise_for_status()
        except HTTPError as e:
            print(f"Se produjo un error: {e.response.json().get('error')}")
        # Procesamiento de la respuesta JSON
        json_data = response.json()

        # Mostrar opciones al usuario
        print("-"*30+f"{table_name.upper()}"+"-"*30)
        for i,row in enumerate(json_data):
            print(str(i+1) + " " + row_string.format(*[row.get(k) for k in keys]))
        print("-"*70)

        # Selección interactiva por índice
        item = input(f"Elija entre las opciones: ")
        print("-"*70)
        try:
            return json_data[int(item)-1]
        except Exception:
            raise IndexError("Error. Introduzca un índice válido.")
    
    def get_available_appointments(id_centro: str,
                                   id_doctor: str,
                                   auth_token: str) -> str|None:
        """
        Obtiene las horas disponibles para citas médicas en una fecha dada.

        La función solicita una fecha al usuario, consulta el servicio de citas
        para recuperar las citas ya existentes del doctor en el centro indicado,
        y permite seleccionar una hora disponible.

        Args:
            id_centro (str): ID del centro médico.
            id_doctor (str): ID del doctor.
            auth_token (str): Token válido para autorización.

        Returns:
            str | None: Fecha y hora seleccionada en formato ISO 8601
                        (YYYY-MM-DDTHH:00:00Z) o None si no hay disponibilidad.
        """
        # Solicitud de fecha al usuario
        fecha: str = input("Elija una fecha (AAAA-MM-DD): ")
        
        # Validación de la fecha
        try:
            datetime.strptime(fecha, "%Y-%m-%d")
        except Exception:
            raise ValueError("Error. Introduzca una fecha válida")
        
        print("-"*70)
        
        # Horario fijo de citas disponibles (horas del día)
        citas_disponibles: set[int] = {8, 9, 10, 11, 12, 13, 15, 16, 17, 18}
        
        # Endpoint del servicio de citas
        url: str = f"{AppUrls.CITAS}/api/v1/citas"
        
        # Cabeceras con token de autorización
        headers: dict[str,str] = {"Content-type": "application/json",
                                  "Authorization": f"Bearer {auth_token}"}
        
        # Parámetros de búsqueda de citas
        body: dict[str, int|str] = {"id_centro": int(id_centro),
                                "id_doctor": int(id_doctor),
                                "fecha": fecha}
        json_body = json.dumps(body)

        # Petición GET
        response = requests.get(url, headers= headers, data= json_body)
        try:
            response.raise_for_status()
        except HTTPError as e:
            print(f"{e.response.json().get('error')}")
        
        citas: dict[str,str] = response.json()
        horas_cita: list[int] = []
        
        # Si existen citas, se eliminan las horas ya ocupadas
        if citas:
            horas: set[int] = set()
            for cita in citas:
                horas.add(int(re.search(r"T(\d{2}):", cita.get('fecha')).group(1)))
            horas_cita = sorted(citas_disponibles.difference(horas))
        else:
            horas_cita = sorted(citas_disponibles)

        # Selección de hora disponible
        if horas_cita:
            print("-"*30+"HORAS DISPONIBLES"+"-"*30)
            for i,h in enumerate(horas_cita):
                print(f"{i+1} - {h}")
            print("-"*70)
            while True:
                h_elegida = input("Elija una hora: ")
                if re.fullmatch(r"^\d*$", h_elegida):
                    h_elegida = int(h_elegida) - 1
                    if h_elegida in range((len(horas_cita))):
                        break
                print("Error. Introduzca un índice válido.")
                print("-"*70)

            return f"{fecha}T{horas_cita[h_elegida]:02d}:00:00Z"
        
           
        # No hay citas disponibles para la fecha seleccionada
        print(f"No hay citas disponibles para el día {fecha}")
        return None

    def create_appointment(fecha: str,
                           motivo: str,
                           estado: str,
                           id_paciente: str,
                           id_doctor: str,
                           id_centro: str,
                           auth_token: str) -> bool:
        """
        Crea una nueva cita médica en el servicio de citas.

        Envía una petición POST al endpoint de citas con la información
        necesaria para registrar una nueva cita médica asociada a un
        paciente, doctor y centro.

        Args:
            fecha (str): Fecha y hora de la cita en formato ISO 8601
                        (YYYY-MM-DDTHH:MM:SSZ).
            motivo (str): Motivo de la consulta médica.
            estado (str): Estado inicial de la cita ("Activa", "Pendiente").
            id_paciente (str): ID del paciente.
            id_doctor (str): ID del doctor.
            id_centro (str): ID del centro médico.
            auth_token (str): Token válido para autorización.

        Returns:
            bool: True si la cita fue creada correctamente,
                False si ocurrió algún error durante la petición.
        """

        # Endpoint del servicio de citas
        url: str = f"{AppUrls.CITAS}/api/v1/citas"

        # Cuerpo de la petición con los datos de la cita
        body: dict[str,str|int] = {
                "fecha": fecha,
                "motivo": motivo,
                "estado": estado,
                "id_paciente": int(id_paciente),
                "id_doctor": int(id_doctor),
                "id_centro": int(id_centro) 
                }
        json_body = json.dumps(body)

        # Cabeceras HTTP con autorización
        headers: dict[str,str] = {"Content-type": "application/json",
                                "Authorization": f"Bearer {auth_token}"}
        
        # Envío de la petición POST
        response = requests.post(url, headers= headers, data= json_body)
        try:
            response.raise_for_status()
        except HTTPError as e:
            print(f"Se produjo un error: {e.response.json().get('error')}")
            return False
        # Cita creada correctamente
        return True
    
    # Selección del centro médico
    while True:
        try:
            centro: dict[str,str] = get_data("centros", token)
            break
        except Exception as e:
            print(e)
    id_centro: str = centro.get("id_centro")
    nombre_centro: str = centro.get("nombre")

    # Selección del doctor
    while True:
        try:
            doctor: dict[str,str] = get_data("doctores", token)
            break
        except Exception as e:
            print(e)
    id_doctor: str = doctor.get("id_doctor")
    apellido_doctor: str = doctor.get("apellido")

    # Selección de la fecha con horas disponibles
    fecha: str = ""
    while not fecha:
        try:
            fecha: str|None = get_available_appointments(id_centro, id_doctor, token)
            break
        except Exception as e:
            print(e)

    # Selección del paciente
    while True:
        try:
            id_paciente: str = get_data("pacientes", token).get("id_paciente")
            break
        except Exception as e:
            print(e)

    # Entrada del motivo de la cita
    motivo: str = input("Indique el motivo de la cita médica: ")
    
    # Creación de la cita médica
    cita: bool = create_appointment(fecha= fecha,
                              motivo= motivo,
                              estado= "Activa",
                              id_paciente= id_paciente,
                              id_doctor= id_doctor,
                              id_centro= id_centro,
                              auth_token= token)
    
    # Muestra por el terminal si la cita fue creada correctamente
    if cita:
        print()
        print(f"Se creo una cita el día {fecha} con el Dr. {apellido_doctor} en el centro {nombre_centro}")