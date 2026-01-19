# POST /citas - Crear nueva cita médica

## Información General

- **Servicio**: citas-service
- **Método**: POST
- **Ruta**: `/citas`
- **Autenticación requerida**: **Sí** 
- **Roles permitidos**: `ADMIN`, `PACIENTE`
- **Content-Type**: application/json

## Descripción

Endpoint para la creación de citas médicas.  
El comportamiento varía según el rol del usuario autenticado:

- **PACIENTE**: Solo puede crear citas para sí mismo y el estado siempre será **"Pendiente"**
- **ADMIN**: Puede crear citas para cualquier paciente y especificar el estado deseado

Realiza validaciones de:
- Existencia de doctor, centro y paciente. También comprueba el estado activo del paciente.
- Disponibilidad horaria (no permite duplicados en misma fecha/hora/doctor/centro salvo que la cita existente esté Cancelada)

## Endpoint Utilizado

```http
POST http://localhost:5002/citas
```

## Requiere token con rol admin o paciente en el header

```json
{
    "Authorization": "Bearer <token>"
}
```

## Ejemplo de Request Body (JSON)

### Paciente

```json
{
  "id_doctor": 1,
  "id_centro": 2,
  "fecha": "2026-02-05T10:00:00Z",
  "motivo": "Caries"
}
```

### Administrador

```json
{
  "id_paciente": 12,
  "id_doctor": 1,
  "id_centro": 2,
  "fecha": "2026-02-05T11:00:00Z",
  "motivo": "Extracción de muela",
  "estado": "Activa"
}
```

## Respuesta esperada (JSON)

### Codigo 201
```json
{"message": "Centros creados con exito"}
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

### Codigo 400 - Existe una cita para la misma fecha/hora/doctor/centro

```json
{
    "message": "Ya hay una cita asignada para el Dr. García en el centro
                Clínica Dental Pamplona Centro para el dia 2026-01-22 a
                las 18:00 horas"
}
```