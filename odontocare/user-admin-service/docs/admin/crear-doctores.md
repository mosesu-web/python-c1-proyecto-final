# POST /admin/doctores - Creación masiva de doctores

## Información General

- **Servicio**: user-admin-service
- **Método**: POST
- **Ruta**: `/admin/doctores`
- **Autenticación requerida**: **SÍ** (solo administradores)
- **Roles permitidos**: `ADMIN`
- **Content-Type**: application/json

## Descripción

Endpoint exclusivo para administradores que permite crear **múltiples doctores** junto con sus usuarios asociados en una sola petición.  

Por cada doctor recibido se crea:
- Un registro en la tabla `doctores`
- Un usuario asociado en la tabla `usuarios` con rol `doctor`

## Endpoint Utilizado

```http
POST http://localhost:5001/admin/doctores
```
## Requiere token con rol admin en el header

```json
{
    "Authorization": "Bearer <token>"
}
```

## Ejemplo de Request Body (JSON)
```json
[
  {
    "nombre": "Carlos",
    "apellido": "Gomez",
    "especialidad": "Ortodoncia"
  },
  {
    "nombre": "Laura",
    "apellido": "Martinez",
    "especialidad": "Endodoncia y Estética Dental"
  },
  {
    "nombre": "Miguel Angel",
    "apellido": "Perez",
    "especialidad": "Periodoncia e Implantes"
  }
]
```

## Respuesta esperada (JSON)

### Codigo 201
```json
{"message": "Doctores creados con exito"}
```

### Codigo 400 - Error de formato JSON o faltante
```json
{"error": "JSON invalido o faltante"}
```

### Codigo 400 - Error de esquema JSON
```json
{
    "error": "Schema de request no válido. El doctor debe contener
              los campos nombre, apellido y especialidad"
}
```

### Codigo 500 - Usuario existente
```json
{"error": "El usuario carlos.gomez ya existe"}
```