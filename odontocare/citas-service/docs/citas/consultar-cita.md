# GET /citas - Obtener listado de citas

## Información General

- **Servicio**: user-admin-service / citas-service
- **Método**: GET
- **Ruta**: `/citas`
- **Autenticación requerida**: **SÍ**
- **Roles permitidos**: `ADMIN`, `MEDICO`, `SECRETARIA`
- **Content-Type**: application/json (excepto para rol doctor, no contiene body)

## Descripción

Endpoint que devuelve el listado de citas médicas según el **rol del usuario** y los **filtros** enviados en el body.

**Comportamiento según rol:**

- **ADMIN** → Puede filtrar por: paciente, doctor, centro, estado y/o fecha
- **SECRETARIA** → Solo puede filtrar por **fecha**
- **MEDICO** → Solo ve **sus propias citas** (no necesita enviar body)

## Endpoint Utilizado

```http
GET http://localhost:5001/citas
```

## Requiere token con rol admin, doctor o secretaria en el header

```json
{
    "Authorization": "Bearer <token>"
}
```

## Ejemplo de Request Body (JSON)

### Administrador

Se pueden hacer combinaciones de campos, no son obligatorios todos

```json
{
  "id_paciente": 14,
  "id_doctor": 7,
  "id_centro": 3,
  "estado": "Activa",
  "fecha": "2026-02-05" // Hora no requerida
}
```

### Secretaria

```json
{
  "fecha": "2026-02-05"
}
```

### Doctor

No se envia nada en el cuerpo de la petición. Se usa el id de usuario contenido en el token para realizar el filtrado


## Respuesta esperada (JSON)

### Codigo 200
```json
[
  {
    "estado": "Activa",
    "fecha": "2026-02-05T09:00:00Z",
    "id_centro": 3,
    "id_cita": 47,
    "id_doctor": 7,
    "id_paciente": 14,
    "id_usuario_registra":10,
    "motivo": "Limpieza y revisión",
  },
  {
    "estado": "Activa",
    "fecha": "2026-02-05T11:00:00Z",
    "id_centro": 3,
    "id_cita": 48,
    "id_doctor": 7,
    "id_paciente": 58,
    "id_usuario_registra":10,
    "motivo": "Entodoncia",
  }
]
```

Si no hay ninguna cita tras el filtrado devuelve

```json
{}
```

### Codigo 400 - Error de formato JSON o faltante
```json
{"error": "JSON invalido o faltante"}
```

### Codigo 400 - Error de esquema JSON
```json
{
	"error": "Schema de request no válido. Faltan campos o son errones"
}
```

### Codigo 400 - Sin campos de filtrado

```json
{
  "error": "Se necesita al menos un parametro de filtrado"
}
```