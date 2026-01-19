# POST /auth/login - Inicio de sesión

## Información General

- **Servicio**: user-admin-service
- **Método**: POST
- **Ruta**: `/auth/login`
- **Autenticación requerida**: **No**
- **Content-Type**: application/json

## Descripción

Endpoint principal para autenticación de usuarios.  
Recibe credenciales (username + password), valida formato, existencia del usuario, estado (para pacientes) y genera token si todo es correcto.

## Endpoint Utilizado

```http
POST http://localhost:5001/auth/login
```

## Ejemplo de Request Body (JSON)

```json
{
  "username": "username",
  "password": "password"
}
```

## Respuesta esperada (JSON)

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwiaWQiOjE1LCJyb2wiOiJPRE9OVE9MT0dPIiwiaWF0IjoxNjE2MjM5MDIyLCJleHAiOjE2MTYyNDI2MjJ9.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
  "expiration": "2026-01-20T01:30:22Z"
}
```