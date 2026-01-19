# POST /admin/pacientes - Creación masiva de pacientes

## Información General

- **Servicio**: user-admin-service
- **Método**: POST
- **Ruta**: `/admin/pacientes`
- **Autenticación requerida**: **SÍ** (solo administradores)
- **Roles permitidos**: `ADMIN`
- **Content-Type**: application/json

## Descripción

Endpoint exclusivo para administradores que permite crear **múltiples pacientes** junto con sus usuarios asociados en una sola petición.  

Por cada paciente recibido se crea:
- Un registro en la tabla `pacientes`
- Un usuario asociado en la tabla `usuarios` con rol `paciente`

## Endpoint Utilizado

```http
POST http://localhost:5001/admin/pacientes
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
    "nombre": "Ana",
    "apellido": "Martinez",
    "telefono": "654321987",
    "estado": "activo"
  },
  {
    "nombre": "Javier",
    "apellido": "Ruiz",
    "telefono": "687654123",
    "estado": "activo"
  },
  {
    "nombre": "María",
    "apellido": "Soto",
    "telefono": "623456789",
    "estado": "inactivo"
  }
]
```

## Respuesta esperada (JSON)

### Codigo 201
```json
{"message": "Pacientes creados con exito"}
```

### Codigo 400 - Error de formato JSON o faltante
```json
{"error": "JSON invalido o faltante"}
```

### Codigo 400 - Error de esquema JSON
```json
{
    "error": "Schema de request no válido. El doctor debe contener
              los campos nombre, apellido, telefono y estado"
}
```

### Codigo 500 - Usuario existente
```json
{"error": "El usuario maria.fernandez ya existe"}
```