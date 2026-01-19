# Imagen base de python
FROM python:3.11-slim

# Establecer directorio de trabajo dentro del container
WORKDIR /app

# Crear un usuario no root y le asigna los permisos al directorio
RUN useradd -m userapp && chown -R userapp:userapp /app


# Copiar e instalar las dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de archivos al directorio de trabajo
COPY . .

# Crear la carpeta para la base de datos
RUN mkdir -p /app/db && chown -R userapp:userapp /app/db && chmod 700 /app/db

# Asegurar que el archivo entrypoint sea ejecutable
RUN chmod +x /app/entrypoint.sh

# Cambiar al usuario no root para ejecutar la app
USER userapp

# Comando de ejecucion del microservicio cuando se inicie el contenedor
ENTRYPOINT [ "/app/entrypoint.sh" ]
CMD ["python", "run.py"]