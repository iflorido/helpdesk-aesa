# 🚁 Helpdesk AESA A2 - Agente de Soporte Técnico

Agente inteligente con memoria para consultas sobre la licencia de drones AESA modalidad A2, utilizando RAG sobre documentación oficial.

## 🎯 Características

- **Chat inteligente** con memoria de conversación por usuario
- **RAG** sobre documentación oficial de AESA
- **Sistema de tickets** con clasificación automática de incidencias
- **Escalado a humano** cuando el agente detecta límites
- **Panel de administración** para gestión de tickets
- **API REST** completa con autenticación JWT

## 🛠 Stack Tecnológico

### Backend
- **FastAPI** - Framework web moderno y rápido
- **SQLAlchemy** - ORM para base de datos
- **PostgreSQL** / SQLite - Base de datos
- **OpenAI API** - Motor del agente inteligente
- **ChromaDB** - Vector store para RAG
- **LangChain** - Orquestación de LLM y RAG

### Frontend
- **React** + Vite
- **Tailwind CSS**
- **React Router**

### DevOps
- **Docker** + Docker Compose
- **Git** para control de versiones
- Deploy en VPS con Plesk

## 📁 Estructura del Proyecto

```
helpdesk-aesa/
├── backend/
│   ├── api/              # Endpoints de la API
│   ├── agent/            # Lógica del agente con tools
│   ├── core/             # Configuración y seguridad
│   │   ├── config.py     # Variables de entorno
│   │   └── security.py   # JWT, hashing
│   ├── db/               # Modelos y repositorios
│   ├── rag/              # Pipeline RAG
│   ├── schemas/          # Pydantic schemas
│   └── main.py           # Aplicación FastAPI
├── frontend/             # Aplicación React
├── docs/                 # PDFs fuente (AESA, manuales)
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🚀 Instalación y Configuración

### Prerrequisitos

- Docker 20.10+
- Docker Compose 2.0+
- Git
- OpenAI API Key

### Método 1: Con Docker (Recomendado) 🐳

#### 1. Clonar el repositorio

```bash
git clone <tu-repositorio>
cd helpdesk-aesa
```

#### 2. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env y añadir tu OPENAI_API_KEY
```

#### 3. Colocar PDFs de AESA

Asegúrate de tener los PDFs en la carpeta `docs/`:
- `Formacion.Subcategoria.A1.A3.pdf`
- `Formacion.Subcategoria.A2.pdf`

#### 4. Iniciar todo

```bash
./start-dev.sh
```

¡Listo! La aplicación estará disponible en:
- **Backend API:** http://localhost:8000
- **Documentación:** http://localhost:8000/docs
- **PostgreSQL:** localhost:5432
- **ChromaDB:** http://localhost:8001

Ver documentación completa de Docker: [DOCKER.md](DOCKER.md)

### Método 2: Sin Docker (Desarrollo Python puro)

<details>
<summary>Click para ver instrucciones sin Docker</summary>

#### Prerrequisitos adicionales
- Python 3.11+
- PostgreSQL instalado localmente

#### Instalación

```bash
# Crear entorno virtual
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar .env
cp ../.env.example ../.env
# Editar .env con tu configuración

# Ejecutar
python main.py
```

Documentación: http://localhost:8000/docs

</details>

## 🐳 Docker

### Desarrollo Local

```bash
# Inicio rápido
./start-dev.sh

# O manualmente
docker-compose up -d

# Ver logs
docker-compose logs -f backend
```

### Producción en VPS

```bash
# Configurar variables de entorno en Plesk primero
docker-compose -f docker-compose.prod.yml up -d --build
```

**Documentación completa de Docker:** Ver [DOCKER.md](DOCKER.md)

## 📚 Documentos AESA

Los PDFs de formación AESA deben estar en la carpeta `docs/`:
- `Formacion.Subcategoria.A1.A3.pdf` - Licencia A1/A3
- `Formacion.Subcategoria.A2.pdf` - Licencia A2

Estos documentos se montan automáticamente en el contenedor y el sistema RAG los procesa para responder consultas.

## 🧪 Testing

```bash
cd backend
pytest
pytest --cov=backend tests/  # Con coverage
```

## 📝 Roadmap

- [x] Estructura base del proyecto
- [x] Configuración y seguridad
- [x] FastAPI con CORS
- [ ] Modelos de base de datos (usuarios, tickets, mensajes)
- [ ] Sistema de autenticación completo
- [ ] Pipeline RAG funcional
- [ ] Agente con tools (buscar docs, escalar, clasificar)
- [ ] API endpoints (chat, tickets, admin)
- [ ] Frontend React
- [ ] Docker Compose completo
- [ ] Deploy en VPS

## 🤝 Contribución

Este es un proyecto personal de aprendizaje. Pull requests son bienvenidos.

## 📄 Licencia

MIT

## 👤 Autor

Desarrollado como proyecto de portfolio para demostrar habilidades en:
- Python avanzado
- FastAPI
- LLMs y RAG
- Arquitectura de agentes
- Docker y despliegue