"""
Punto de entrada principal de la app Flask

Crea la applicación  y la configura a traves de las variables
definidas en Config.
"""

from app import create_app
from config import Config

# Creación de la instancia de la aplicación
app = create_app()

if __name__ == "__main__":
    # host= 0.0.0.0 permite que la app sea accesible fuera del contenedor
    app.run(host= "0.0.0.0", port= Config.PORT, debug= Config.DEBUG) 