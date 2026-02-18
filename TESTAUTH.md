# 🔐 Pruebas de Autenticación

Guía para probar el sistema de autenticación con ejemplos completos.

## 📋 Endpoints Disponibles

Con el servidor corriendo en `http://localhost:8000`:

| Endpoint | Método | Auth | Descripción |
|----------|--------|------|-------------|
| `/api/auth/register` | POST | No | Registrar nuevo usuario |
| `/api/auth/login` | POST | No | Iniciar sesión |
| `/api/auth/me` | GET | Sí | Ver perfil |
| `/api/auth/test-auth` | GET | Sí | Probar token |

## 🧪 Probar con la Documentación Interactiva

La forma más fácil es usar Swagger UI:

1. Abre en tu navegador: **http://localhost:8000/docs**
2. Verás todos los endpoints con formularios interactivos
3. Puedes probar directamente desde ahí

## 💻 Probar con cURL

### 1. Registrar un usuario

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "juan@example.com",
    "password": "password123",
    "full_name": "Juan Pérez"
  }'
```

**Respuesta esperada:**
```json
{
  "email": "juan@example.com",
  "full_name": "Juan Pérez",
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "is_active": true,
  "is_admin": false,
  "created_at": "2026-02-18T13:45:00",
  "updated_at": "2026-02-18T13:45:00"
}
```

### 2. Iniciar sesión

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "juan@example.com",
    "password": "password123"
  }'
```

**Respuesta esperada:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**⚠️ IMPORTANTE:** Copia el `access_token` para los siguientes pasos.

### 3. Ver perfil (requiere token)

```bash
# Reemplaza YOUR_TOKEN_HERE con el token del paso anterior
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Respuesta esperada:**
```json
{
  "email": "juan@example.com",
  "full_name": "Juan Pérez",
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "is_active": true,
  "is_admin": false,
  "created_at": "2026-02-18T13:45:00",
  "updated_at": "2026-02-18T13:45:00"
}
```

### 4. Probar autenticación

```bash
curl -X GET "http://localhost:8000/api/auth/test-auth" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Respuesta esperada:**
```json
{
  "message": "Autenticación exitosa",
  "user_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

## 🐍 Probar con Python

Crea un archivo `test_auth.py`:

```python
import requests

BASE_URL = "http://localhost:8000/api/auth"

# 1. Registrar usuario
print("1️⃣ Registrando usuario...")
register_data = {
    "email": "test@example.com",
    "password": "password123",
    "full_name": "Usuario de Prueba"
}
response = requests.post(f"{BASE_URL}/register", json=register_data)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}\n")

# 2. Login
print("2️⃣ Iniciando sesión...")
login_data = {
    "email": "test@example.com",
    "password": "password123"
}
response = requests.post(f"{BASE_URL}/login", json=login_data)
token_data = response.json()
access_token = token_data["access_token"]
print(f"Status: {response.status_code}")
print(f"Token: {access_token[:50]}...\n")

# 3. Ver perfil
print("3️⃣ Obteniendo perfil...")
headers = {"Authorization": f"Bearer {access_token}"}
response = requests.get(f"{BASE_URL}/me", headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}\n")

# 4. Test auth
print("4️⃣ Probando autenticación...")
response = requests.get(f"{BASE_URL}/test-auth", headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}\n")

print("✅ Todas las pruebas completadas!")
```

Ejecuta:
```bash
python test_auth.py
```

## 🔍 Verificar en la Base de Datos

```bash
psql -U postgres -d aesa_agent

-- Ver usuarios creados
SELECT id, email, full_name, is_active, is_admin, created_at FROM users;

-- Ver detalles de un usuario
SELECT * FROM users WHERE email = 'juan@example.com';
```

## ❌ Casos de Error

### Email ya registrado
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "juan@example.com",
    "password": "password123",
    "full_name": "Juan Duplicado"
  }'
```

**Respuesta:**
```json
{
  "detail": "El email ya está registrado"
}
```

### Credenciales incorrectas
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "juan@example.com",
    "password": "wrongpassword"
  }'
```

**Respuesta:**
```json
{
  "detail": "Email o contraseña incorrectos"
}
```

### Sin token
```bash
curl -X GET "http://localhost:8000/api/auth/me"
```

**Respuesta:**
```json
{
  "detail": "Not authenticated"
}
```

### Token inválido
```bash
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer token_invalido"
```

**Respuesta:**
```json
{
  "detail": "No se pudieron validar las credenciales"
}
```

## 🎯 Próximos Pasos

Una vez que la autenticación funcione:

1. ✅ Crear endpoints de tickets
2. ✅ Crear endpoints de chat
3. ✅ Implementar el agente con OpenAI
4. ✅ Pipeline RAG para los PDFs de AESA
5. ✅ Frontend React

## 💡 Tips

- El token JWT expira en 30 minutos (configurable en `.env` con `ACCESS_TOKEN_EXPIRE_MINUTES`)
- Los tokens son stateless - no se guardan en la base de datos
- Usa HTTPS en producción para proteger los tokens
- El hash de contraseña usa bcrypt (muy seguro)