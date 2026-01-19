"""
Funciones auxiliares de la app

Generación de  contraseñas aleatorias para la creación de usuarios
"""

import string
import random

def random_password(password_lenght: int= 8) -> str:
    """
    Genera una contraseña aleatoria con una mezcla de letras
    minúsculas, mayúsculas, números y símbolos.

    Args:
        password_length (int): Longitud total de la contraseña. Por defecto es 8.
    """
    password: list[str] = []
    s1: list[str] = list(string.ascii_lowercase)  # Letras minúsculas
    s2: list[str] = list(string.ascii_uppercase)  # Letras mayúsculas
    s3: list[str] = list(string.digits)  # Números
    s4: list[str] = list(string.punctuation)  # Simbolos

    # Mezcla aleatoria de las listas
    random.shuffle(s1)
    random.shuffle(s2)
    random.shuffle(s3)
    random.shuffle(s4)

    # Añade 30% de letras minúsculas y 30% de letras mayusculas a la contraseña
    for i in range(round(password_lenght*0.3)):
        password.append(s1[i])
        password.append(s2[i])
    
    # Añade 20% de números y 20% de simbolos
    for i in range(round(password_lenght*0.2)):
        password.append(s3[i])
        password.append(s4[i])
    
    # Mezcla final de la contraseña
    random.shuffle(password)
    
    # Se combinan los caracteres en un único string
    return "".join(password)