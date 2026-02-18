# 🏠 Setup Local - Helpdesk AESA A2

Configuración específica para desarrollo local sin Docker.

## 📋 Tu Configuración Local

### Base de datos PostgreSQL
- **Base de datos:** `aesa_agent`
- **Usuario:** `postgres`
- **Host:** `localhost:5432`
- **Contraseña:** (tu contraseña de postgres local)

### PDFs disponibles
- `docs/Formacion.Subcategoria.A1.A3.pdf` - Licencia A1/A3
- `docs/Formacion.Subcategoria.A2.pdf` - Licencia A2

## 🚀 Inicio Rápido

### 1. Configurar `.env`

```bash
cp .env.example .env
```

Edita `.env` y configura:

```env
# OpenAI
OPENAI_API_KEY=sk-tu-api-key-aqui

# Database local
DATABASE_URL=postgresql://postgres:tu-password@localhost:5432/aesa_agent

# Security (se auto-genera si no lo cambias)
SECRET_KEY=your-secret-key-here-generate-with-openssl-rand-hex-32
```

### 2. Ejecutar el script de inicio

```bash
./start-dev.sh
```

Este script automáticamente:
- ✅ Verifica que `.env` existe y está configurado
- ✅ Genera `SECRET_KEY` si no existe
- ✅ Crea entorno virtual si no existe (o usa tu conda)
- ✅ Instala dependencias Python
- ✅ Verifica conexión a PostgreSQL
- ✅ Verifica que existen los PDFs
- ✅ Inicia FastAPI con uvicorn

### 3. Acceder a la aplicación

Una vez iniciado:
- **API:** http://localhost:8000
- **Documentación interactiva:** http://localhost:8000/docs
- **Health check:** http://localhost:8000/health

## 🔧 Alternativa: Inicio Manual

Si prefieres iniciar manualmente:

```bash
# 1. Activar entorno (si usas venv)
source backend/venv/bin/activate

# 2. O activar conda
conda activate tu-entorno

# 3. Instalar dependencias
cd backend
pip install -r requirements.txt

# 4. Iniciar servidor
python main.py

# O con uvicorn directamente
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📁 Estructura de Directorios

```
helpdesk-aesa/
├── .env                    # Tu configuración local (NO commitear)
├── .env.example            # Plantilla
├── start-dev.sh            # Script de inicio
├── README.md
├── docs/                   # PDFs de AESA
│   ├── Formacion.Subcategoria.A1.A3.pdf
│   └── Formacion.Subcategoria.A2.pdf
├── backend/
│   ├── venv/              # Entorno virtual (si no usas conda)
│   ├── core/
│   │   ├── config.py      # Lee variables de .env
│   │   └── security.py
│   ├── main.py
│   └── requirements.txt
├── logs/                  # Logs de la aplicación
└── chroma_data/          # Base de datos vectorial local
```

## 🗄️ Crear Base de Datos

Si aún no has creado la base de datos `aesa_agent`:

```bash
# Conectar a PostgreSQL
psql -U postgres

# Crear la base de datos
CREATE DATABASE aesa_agent;

# Verificar
\l

# Salir
\q
```

## 🧪 Verificar que Todo Funciona

### Test 1: Endpoint raíz
```bash
curl http://localhost:8000
```

Deberías ver:
```json
{
  "message": "Bienvenido a Helpdesk AESA A2",
  "version": "0.1.0",
  "environment": "development",
  "docs": "/docs"
}
```

### Test 2: Health check
```bash
curl http://localhost:8000/health
```

### Test 3: Documentación interactiva
Abre en tu navegador: http://localhost:8000/docs

## 🐛 Troubleshooting

### Error: "No module named 'fastapi'"
```bash
cd backend
pip install -r requirements.txt
```

### Error: "could not connect to server"
- Verifica que PostgreSQL está corriendo: `pg_isready`
- Verifica el usuario y contraseña en `.env`
- Verifica que la base de datos `aesa_agent` existe

### Error: "OPENAI_API_KEY validation error"
- Asegúrate de que tu API key comienza con `sk-`
- Verifica que está en `.env` como: `OPENAI_API_KEY=sk-...`

### Los PDFs no se encuentran
- Verifica que están en `docs/` en la raíz del proyecto
- Los nombres deben coincidir exactamente

## 📝 Próximos Pasos

Una vez que tengas el servidor corriendo:

1. **Crear modelos de base de datos** (usuarios, tickets, mensajes)
2. **Implementar el pipeline RAG** para procesar los PDFs
3. **Crear el agente** con tools (buscar docs, escalar, clasificar)
4. **Desarrollar los endpoints de la API** (chat, tickets, admin)
5. **Frontend React** (cuando backend esté estable)

## 🚢 Deploy a Producción

Cuando estés listo para producción, consulta: [DOCKER_PRODUCTION.md](DOCKER_PRODUCTION.md)