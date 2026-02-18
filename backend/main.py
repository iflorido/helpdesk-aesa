"""
Aplicación principal de FastAPI para Helpdesk AESA A2.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import sys
from pathlib import Path

# Añadir el directorio backend al path para imports relativos
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from core.config import settings

# Configurar logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestor de ciclo de vida de la aplicación.
    Reemplaza los eventos deprecados startup/shutdown.
    """
    # Startup
    logger.info(f"✅ Iniciando {settings.PROJECT_NAME}")
    logger.info(f"📍 Entorno: {settings.ENVIRONMENT}")
    logger.info(f"🔧 Debug: {settings.DEBUG}")
    # Aquí inicializaremos la base de datos, ChromaDB, etc.
    
    yield
    
    # Shutdown
    logger.info(f"🛑 Cerrando {settings.PROJECT_NAME}")
    # Aquí cerraremos conexiones, recursos, etc.


# Crear aplicación FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Agente de soporte técnico con memoria para consultas sobre licencia AESA A2",
    version="0.1.0",
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Endpoint raíz para verificar que el servidor está funcionando."""
    return {
        "message": f"Bienvenido a {settings.PROJECT_NAME}",
        "version": "0.1.0",
        "environment": settings.ENVIRONMENT,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Endpoint de health check para monitoreo."""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }


# Incluir routers
from api.auth import router as auth_router
from api.tickets import router as tickets_router
from api.chat import router as chat_router

app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])
app.include_router(tickets_router, prefix="/api/tickets", tags=["tickets"])
app.include_router(chat_router, prefix="/api/chat", tags=["chat"])


# Manejador global de excepciones
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Maneja excepciones no capturadas."""
    logger.error(f"Error no manejado: {exc}", exc_info=True)
    
    if settings.DEBUG:
        return JSONResponse(
            status_code=500,
            content={
                "detail": str(exc),
                "type": type(exc).__name__
            }
        )
    
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor"}
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )