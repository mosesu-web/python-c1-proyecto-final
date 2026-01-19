# PUT /citas/<id> - Cancelar cita

## Información General

- **Servicio**: citas-service
- **Método**: PUT
- **Ruta**: `/citas/<id>`
- **Autenticación requerida**: **Sí**
- **Roles permitidos**: `ADMIN`, `SECRETARIA`
- **Content-Type**: application/json

## Descripción

Endpoint para **cancelar** una cita médica existente.  
Solo usuarios con rol **Administrador** o **Secretaria** pueden realizar esta acción.

## Endpoint Utilizado

```http
PUT http://localhost:5001/citas/1
```

## Requiere token con rol admin o secretaria en el header

```json
{
    "Authorization": "Bearer <token>"
}
```

## Parametros de la url

| Nomber | Tipo | Descripción |
|--------------|--------------|--------------|
|`id`|Integer|ID de la cita a cancelar|

## Request Body

No requiere un cuerpo en la petición

## Respuesta esperada (JSON)

### Codigo 200

```json
{"message": "Cita cancelada"}
```

Si la cita ya estaba cancelada devuelve

```json
{"message": "La cita ya estaba cancelada"}
```

### Codigo 404 - Cita no encontrada

Lanza un error 404 en texto plano si no encuentra la cita


