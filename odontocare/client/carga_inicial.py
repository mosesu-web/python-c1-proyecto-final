"""
Ciente de carga inicial de datos y creación de citas.

Este script permite:
1. Realizar login en el sistema hasta obtener un token válido.
2. Cargar datos iniciales desde archivo CSV.
3. Crear citas médicas utilizando el token de autenticación.
4. Permitir al usuario crear múltiples citas de manera interactiva.

Funciones utilizadas:
- login(): Realiza la autenticación y devuelve un token.
- read_load_data(token): Carga los datos iniciales necesarios para el sistema desde CSV.
- create_appointment(token): Crea una cita médica usando el token.
"""

from utils import login, read_load_data, create_appointment

# Cargar datos iniciales solo la primera vez

if __name__ == "__main__":

    # Token de autenticación inicial
    token: str = ""
    
    while True:
        # Intentar login hasta obtener un token
        while not token:
            try:
                token = login()
            except Exception as e:
                # Tipo de error si no se consigue hacer login
                print(f"{e.response}")
        
        # Cargar datos iniciales solo si el usuario lo desea
        cargar_datos: bool = input("¿Desea volcar los datos locales? (S/N)").lower() == 's'
        
        if cargar_datos:     
            # Indicar si se deben cargar los datos iniciales
            read_load_data(token)
            cargar_datos = False
        
        # Crear una cita
        create_appointment(token)
        print()
        
        # Preguntar al usuario si desea crear otra cita
        continuar = input("Desea crear otra cita (S/N)?")
        if continuar not in "Ss":
            break