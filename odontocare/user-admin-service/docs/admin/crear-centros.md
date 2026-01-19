# POST /admin/centros - Creación masiva de clinicas

## Información General

- **Servicio**: user-admin-service
- **Método**: POST
- **Ruta**: `/admin/centros`
- **Autenticación requerida**: **SÍ** (solo administradores)
- **Roles permitidos**: `ADMIN`
- **Content-Type**: application/json

## Descripción

Endpoint exclusivo para administradores que permite crear **múltiples clinicas dentales** en una sola petición.

## Endpoint Utilizado

```http
POST http://localhost:5001/admin/centros
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
    "nombre": "Clínica Dental Pamplona Centro",
    "direccion": "Calle Mayor 12, 31001 Pamplona, Navarra"
  },
  {
    "nombre": "OdontoCare Norte",
    "direccion": "Av. Carlos III 45, 31620 Huarte"
  },
  {
    "nombre": "Clínica Sonrisas Tudela",
    "direccion": "Plaza de los Fueros 3, 31500 Tudela, Navarra"
  }
]
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
    "error": "Schema de request no válido. El doctor debe contener
              los campos nombre y dirección"
}
```