# 🎫 Pruebas de Tickets y Chat

Guía para probar el sistema de tickets y chat.

## 📋 Endpoints Disponibles

### Tickets
| Endpoint | Método | Auth | Descripción |
|----------|--------|------|-------------|
| `/api/tickets/` | POST | Sí | Crear ticket |
| `/api/tickets/` | GET | Sí | Listar mis tickets |
| `/api/tickets/{id}` | GET | Sí | Ver ticket |
| `/api/tickets/{id}` | PATCH | Sí | Actualizar ticket |
| `/api/tickets/{id}/close` | POST | Sí | Cerrar ticket |

### Chat
| Endpoint | Método | Auth | Descripción |
|----------|--------|------|-------------|
| `/api/chat/{ticket_id}/messages` | POST | Sí | Enviar mensaje |
| `/api/chat/{ticket_id}/messages` | GET | Sí | Ver historial |
| `/api/chat/{ticket_id}/conversation` | GET | Sí | Conversación (formato agente) |

## 🧪 Flujo de Prueba Completo

### 1. Autenticarse (obtener token)

```bash
# Login
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

Copia el `access_token` para usarlo en los siguientes pasos.

**Variable de entorno para facilitar:**
```bash
export TOKEN="tu-token-aqui"
```

### 2. Crear un ticket

```bash
curl -X POST "http://localhost:8000/api/tickets/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "¿Qué distancia debo mantener de zonas habitadas?",
    "category": "licensing"
  }'
```

**Respuesta esperada:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "...",
  "title": "¿Qué distancia debo mantener de zonas habitadas?",
  "status": "open",
  "priority": "medium",
  "category": "licensing",
  "message_count": 0,
  "created_at": "2026-02-18T14:00:00",
  "updated_at": "2026-02-18T14:00:00"
}
```

**⚠️ Importante:** Copia el `id` del ticket para los siguientes pasos.

```bash
export TICKET_ID="el-id-del-ticket"
```

### 3. Enviar mensaje en el ticket

```bash
curl -X POST "http://localhost:8000/api/chat/$TICKET_ID/messages" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Voy a volar mi dron A2 cerca de una urbanización, ¿qué precauciones debo tomar?"
  }'
```

**Respuesta esperada:**
```json
{
  "id": "msg-123...",
  "ticket_id": "...",
  "role": "user",
  "content": "Voy a volar mi dron A2 cerca de una urbanización...",
  "metadata": null,
  "created_at": "2026-02-18T14:01:00",
  "updated_at": "2026-02-18T14:01:00"
}
```

### 4. Ver historial del chat

```bash
curl -X GET "http://localhost:8000/api/chat/$TICKET_ID/messages" \
  -H "Authorization: Bearer $TOKEN"
```

**Respuesta esperada:**
```json
{
  "ticket_id": "...",
  "messages": [
    {
      "id": "...",
      "role": "user",
      "content": "Voy a volar mi dron A2...",
      "created_at": "2026-02-18T14:01:00"
    }
  ],
  "total_messages": 1
}
```

### 5. Listar mis tickets

```bash
curl -X GET "http://localhost:8000/api/tickets/" \
  -H "Authorization: Bearer $TOKEN"
```

**Respuesta esperada:**
```json
{
  "tickets": [
    {
      "id": "...",
      "title": "¿Qué distancia debo mantener de zonas habitadas?",
      "status": "open",
      "priority": "medium",
      "message_count": 1,
      "created_at": "2026-02-18T14:00:00"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20
}
```

### 6. Actualizar ticket (cambiar prioridad)

```bash
curl -X PATCH "http://localhost:8000/api/tickets/$TICKET_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "priority": "high"
  }'
```

### 7. Cerrar ticket

```bash
curl -X POST "http://localhost:8000/api/tickets/$TICKET_ID/close" \
  -H "Authorization: Bearer $TOKEN"
```

## 🌐 Pruebas con Swagger UI

La forma más fácil de probar:

1. Abre: **http://localhost:8000/docs**
2. Haz click en **"Authorize"** (candado verde arriba a la derecha)
3. Pega tu token en el formato: `Bearer tu-token-aqui`
4. Ahora puedes probar todos los endpoints desde la interfaz gráfica

## 🐍 Script de Prueba en Python

```python
import requests
from uuid import UUID

BASE_URL = "http://localhost:8000/api"

# 1. Login
print("1️⃣ Login...")
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"email": "test@example.com", "password": "password123"}
)
token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print(f"Token obtenido: {token[:30]}...\n")

# 2. Crear ticket
print("2️⃣ Creando ticket...")
ticket_response = requests.post(
    f"{BASE_URL}/tickets/",
    headers=headers,
    json={
        "title": "Consulta sobre altura máxima de vuelo",
        "category": "technical"
    }
)
ticket = ticket_response.json()
ticket_id = ticket["id"]
print(f"Ticket creado: {ticket_id}")
print(f"Estado: {ticket['status']}\n")

# 3. Enviar mensaje
print("3️⃣ Enviando mensaje...")
message_response = requests.post(
    f"{BASE_URL}/chat/{ticket_id}/messages",
    headers=headers,
    json={"content": "¿Cuál es la altura máxima permitida para drones A2?"}
)
message = message_response.json()
print(f"Mensaje enviado: {message['id']}\n")

# 4. Ver historial
print("4️⃣ Obteniendo historial...")
history_response = requests.get(
    f"{BASE_URL}/chat/{ticket_id}/messages",
    headers=headers
)
history = history_response.json()
print(f"Total de mensajes: {history['total_messages']}")
for msg in history['messages']:
    print(f"  [{msg['role']}]: {msg['content'][:50]}...\n")

# 5. Listar tickets
print("5️⃣ Listando tickets...")
tickets_response = requests.get(
    f"{BASE_URL}/tickets/",
    headers=headers
)
tickets_data = tickets_response.json()
print(f"Total de tickets: {tickets_data['total']}")
for t in tickets_data['tickets']:
    print(f"  - {t['title']} [{t['status']}] - {t['message_count']} mensajes\n")

# 6. Cerrar ticket
print("6️⃣ Cerrando ticket...")
close_response = requests.post(
    f"{BASE_URL}/tickets/{ticket_id}/close",
    headers=headers
)
closed_ticket = close_response.json()
print(f"Ticket cerrado. Estado: {closed_ticket['status']}")
print(f"Cerrado en: {closed_ticket['closed_at']}\n")

print("✅ Todas las pruebas completadas!")
```

## 📊 Filtros y Paginación

### Filtrar tickets por estado

```bash
# Solo tickets abiertos
curl -X GET "http://localhost:8000/api/tickets/?status_filter=open" \
  -H "Authorization: Bearer $TOKEN"

# Solo tickets cerrados
curl -X GET "http://localhost:8000/api/tickets/?status_filter=closed" \
  -H "Authorization: Bearer $TOKEN"
```

### Paginación

```bash
# Página 1, 10 tickets por página
curl -X GET "http://localhost:8000/api/tickets/?page=1&page_size=10" \
  -H "Authorization: Bearer $TOKEN"

# Página 2
curl -X GET "http://localhost:8000/api/tickets/?page=2&page_size=10" \
  -H "Authorization: Bearer $TOKEN"
```

## 🔍 Verificar en la Base de Datos

```bash
psql -U postgres -d aesa_agent

-- Ver tickets
SELECT id, title, status, priority, created_at FROM tickets;

-- Ver mensajes de un ticket
SELECT role, content, created_at FROM messages 
WHERE ticket_id = 'id-del-ticket'
ORDER BY created_at ASC;

-- Contar mensajes por ticket
SELECT t.title, COUNT(m.id) as message_count
FROM tickets t
LEFT JOIN messages m ON t.id = m.ticket_id
GROUP BY t.id, t.title;
```

## ❌ Casos de Error

### Intentar enviar mensaje en ticket cerrado

```bash
# Primero cerrar el ticket, luego intentar enviar mensaje
curl -X POST "http://localhost:8000/api/chat/$TICKET_ID/messages" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "Otro mensaje"}'
```

**Respuesta:**
```json
{
  "detail": "No puedes enviar mensajes en un ticket cerrado"
}
```

### Intentar acceder a ticket de otro usuario

Si otro usuario intenta acceder a tu ticket, recibirá:
```json
{
  "detail": "No tienes permiso para ver este ticket"
}
```

## 🎯 Próximos Pasos

Una vez que tickets y chat funcionen:

1. ✅ Integrar el agente OpenAI para respuestas automáticas
2. ✅ Pipeline RAG para buscar en los PDFs de AESA
3. ✅ Sistema de clasificación automática de tickets
4. ✅ Detección de cuando escalar a humano
5. ✅ Frontend React

## 💡 Notas

- Los tickets se crean en estado `open` con prioridad `medium` por defecto
- El conteo de mensajes se actualiza automáticamente
- Los tickets tienen timestamps de `escalated_at` y `closed_at` cuando cambian de estado
- El formato de conversación (`/conversation` endpoint) está optimizado para enviarse directamente al LLM