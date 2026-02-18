# 🗄️ Base de Datos - Helpdesk AESA A2

Guía completa para trabajar con la base de datos, modelos y migraciones.

## 📊 Estructura de Datos

### Tablas

```
users
├── id (UUID)
├── email (unique)
├── hashed_password
├── full_name
├── is_active
├── is_admin
├── created_at
└── updated_at

tickets
├── id (UUID)
├── user_id (FK → users)
├── title
├── status (open, in_progress, escalated, closed)
├── priority (low, medium, high, urgent)
├── category (technical, licensing, general, documentation)
├── escalated_at
├── closed_at
├── created_at
└── updated_at

messages
├── id (UUID)
├── ticket_id (FK → tickets)
├── role (user, assistant, system)
├── content
├── metadata (JSONB)
├── created_at
└── updated_at

documents
├── id (UUID)
├── filename (unique)
├── file_path
├── document_type (pdf_aesa_a1, pdf_aesa_a2, pdf_aesa_a3, manual, faq, other)
├── processed
├── vector_count
├── file_size
├── page_count
├── uploaded_at
└── processed_at
```

## 🚀 Inicialización Rápida

### Opción 1: Crear tablas directamente (desarrollo rápido)

```bash
cd backend
python init_db.py
```

Esto crea todas las tablas en tu base de datos PostgreSQL local.

### Opción 2: Usar Alembic (recomendado para producción)

```bash
cd backend

# 1. Crear la primera migración
alembic revision --autogenerate -m "Initial migration"

# 2. Aplicar la migración
alembic upgrade head

# 3. Verificar
alembic current
```

## 🔧 Trabajar con Migraciones de Alembic

### Crear una nueva migración

Cada vez que cambies los modelos:

```bash
# Generar migración automáticamente
alembic revision --autogenerate -m "Descripción del cambio"

# Aplicar la migración
alembic upgrade head
```

### Comandos útiles

```bash
# Ver el estado actual
alembic current

# Ver historial de migraciones
alembic history

# Hacer downgrade (revertir última migración)
alembic downgrade -1

# Hacer downgrade a una versión específica
alembic downgrade <revision_id>

# Upgrade a una versión específica
alembic upgrade <revision_id>

# Ver SQL sin ejecutar
alembic upgrade head --sql
```

### Ejemplo: Añadir un nuevo campo

1. Edita el modelo (ej: `db/models/user.py`):
```python
class User(Base):
    # ... campos existentes ...
    phone_number = Column(String(20), nullable=True)  # Nuevo campo
```

2. Genera la migración:
```bash
alembic revision --autogenerate -m "Add phone_number to users"
```

3. Revisa el archivo generado en `alembic/versions/`

4. Aplica la migración:
```bash
alembic upgrade head
```

## 💡 Uso de los Modelos

### Crear un usuario

```python
from db import SessionLocal, User
from core.security import get_password_hash

db = SessionLocal()

user = User(
    email="usuario@example.com",
    hashed_password=get_password_hash("password123"),
    full_name="Juan Pérez",
    is_active=True,
    is_admin=False
)

db.add(user)
db.commit()
db.refresh(user)

print(f"Usuario creado: {user.id}")
db.close()
```

### Crear un ticket con mensajes

```python
from db import SessionLocal, Ticket, Message, TicketStatus, MessageRole
import uuid

db = SessionLocal()

# Crear ticket
ticket = Ticket(
    user_id=uuid.UUID("id-del-usuario"),
    title="Consulta sobre licencia A2",
    status=TicketStatus.OPEN,
    priority=TicketPriority.MEDIUM,
    category=TicketCategory.LICENSING
)

db.add(ticket)
db.commit()
db.refresh(ticket)

# Añadir mensaje del usuario
message_user = Message(
    ticket_id=ticket.id,
    role=MessageRole.USER,
    content="¿Qué distancia debo mantener de zonas habitadas?"
)

# Añadir respuesta del asistente
message_assistant = Message(
    ticket_id=ticket.id,
    role=MessageRole.ASSISTANT,
    content="Según el reglamento AESA...",
    metadata={
        "sources": ["Formacion.Subcategoria.A2.pdf"],
        "tokens_used": 150
    }
)

db.add_all([message_user, message_assistant])
db.commit()

db.close()
```

### Consultar tickets de un usuario

```python
from db import SessionLocal, Ticket, TicketStatus

db = SessionLocal()

# Tickets abiertos de un usuario
tickets = db.query(Ticket).filter(
    Ticket.user_id == user_id,
    Ticket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS])
).order_by(Ticket.created_at.desc()).all()

for ticket in tickets:
    print(f"Ticket: {ticket.title}")
    print(f"Mensajes: {ticket.message_count}")
    
    for message in ticket.messages:
        print(f"  [{message.role}]: {message.content[:50]}...")

db.close()
```

### Registrar un documento procesado

```python
from db import SessionLocal, Document, DocumentType
from datetime import datetime

db = SessionLocal()

document = Document(
    filename="Formacion.Subcategoria.A2.pdf",
    file_path="/app/docs/Formacion.Subcategoria.A2.pdf",
    document_type=DocumentType.PDF_AESA_A2,
    processed=True,
    vector_count=150,
    file_size=2048576,
    page_count=45,
    processed_at=datetime.utcnow()
)

db.add(document)
db.commit()

db.close()
```

## 🎯 Patrones Comunes

### Dependency Injection en FastAPI

```python
from fastapi import Depends
from sqlalchemy.orm import Session
from db import get_db

@app.get("/tickets")
async def list_tickets(db: Session = Depends(get_db)):
    tickets = db.query(Ticket).all()
    return tickets
```

### Usar transacciones

```python
from db import SessionLocal

db = SessionLocal()
try:
    # Operaciones
    user = User(...)
    db.add(user)
    
    ticket = Ticket(user_id=user.id, ...)
    db.add(ticket)
    
    # Commit si todo sale bien
    db.commit()
except Exception as e:
    # Rollback si hay error
    db.rollback()
    raise e
finally:
    db.close()
```

## 🐛 Troubleshooting

### Error: "relation does not exist"

Las tablas no existen. Ejecuta:
```bash
python init_db.py
# o
alembic upgrade head
```

### Error: "column does not exist"

La base de datos no está sincronizada con los modelos. Genera y aplica una migración:
```bash
alembic revision --autogenerate -m "Sync database"
alembic upgrade head
```

### Ver el SQL generado por una query

```python
from sqlalchemy import inspect

query = db.query(User).filter(User.email == "test@example.com")
print(str(query))
```

### Reset completo de la base de datos

⚠️ **CUIDADO**: Esto borra todos los datos.

```bash
# En PostgreSQL
psql -U postgres
DROP DATABASE aesa_agent;
CREATE DATABASE aesa_agent;
\q

# Recrear tablas
python init_db.py
```

## 📝 Próximos Pasos

Una vez tengas la base de datos inicializada:

1. **Crear endpoints de autenticación** (registro, login)
2. **Crear endpoints de tickets** (crear, listar, actualizar)
3. **Crear endpoints de chat** (enviar mensaje, obtener historial)
4. **Implementar el agente** que use estos modelos
5. **Pipeline RAG** para procesar los documentos

## 🔗 Referencias

- [SQLAlchemy ORM](https://docs.sqlalchemy.org/en/20/orm/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [FastAPI with Databases](https://fastapi.tiangolo.com/tutorial/sql-databases/)