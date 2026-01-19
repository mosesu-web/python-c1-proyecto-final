# POST /admin/usuarios - Creación masiva de usuarios

## Información General

- **Servicio**: user-admin-service
- **Método**: POST
- **Ruta**: `/admin/usuarios`
- **Autenticación requerida**: **SÍ** (solo administradores)
- **Roles permitidos**: `ADMIN`
- **Content-Type**: application/json

## Descripción

Endpoint exclusivo para administradores que permite crear **múltiples usuarios** en una sola petición.

## Endpoint Utilizado

```http
POST http://localhost:5001/admin/usuarios
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
    "username": "doctor.lopez",
    "password": "Clinica2025!",
    "rol": "doctor"
  },
  {
    "username": "asistente.maria",
    "password": "Asist2026$",
    "rol": "secretaria"
  },
  {
    "username": "paciente.juan456",
    "password": "MiClaveSegura789",
    "rol": "paciente"
  }
]
```

## Respuesta esperada (JSON)

### Codigo 201
```json
{"message": "Usuarios creados con exito"}
```

### Codigo 400 - Error de formato JSON o faltante
```json
{"error": "JSON invalido o faltante"}
```

### Codigo 400 - Error de esquema JSON
```json
{
    "error": "Schema de request no válido. El usuario debe contener
              los campos  username, password y rol"
}
```

### Codigo 500 - Usuario existente
```json
{"error": "El usuario admin ya existe"}
```