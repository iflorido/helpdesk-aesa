"""
Configuración centralizada de la aplicación usando Pydantic Settings.
Lee variables de entorno desde .env automáticamente.
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Configuración principal de la aplicación."""
    
    # Database
    DATABASE_URL: str = Field(
        default="sqlite:///./helpdesk.db",
        description="URL de conexión a la base de datos"
    )
    
    # OpenAI API
    OPENAI_API_KEY: str = Field(
        default="",
        description="API Key de OpenAI para el agente"
    )
    
    # Security
    SECRET_KEY: str = Field(
        default="default-secret-key-change-in-production",
        description="Clave secreta para JWT (generar con: openssl rand -hex 32)"
    )
    ALGORITHM: str = Field(
        default="HS256",
        description="Algoritmo para JWT"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        description="Minutos de expiración del token de acceso"
    )
    
    # CORS
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="Orígenes permitidos para CORS"
    )
    
    # ChromaDB
    CHROMA_HOST: str = Field(
        default="localhost",
        description="Host de ChromaDB"
    )
    CHROMA_PORT: int = Field(
        default=8001,
        description="Puerto de ChromaDB"
    )
    CHROMA_PERSIST_DIRECTORY: str = Field(
        default="./chroma_data",
        description="Directorio para persistir ChromaDB"
    )
    
    # Application
    ENVIRONMENT: str = Field(
        default="development",
        description="Entorno de la aplicación (development, production)"
    )
    DEBUG: bool = Field(
        default=True,
        description="Modo debug"
    )
    PROJECT_NAME: str = Field(
        default="Helpdesk AESA A2",
        description="Nombre del proyecto"
    )
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(
        default=60,
        description="Límite de peticiones por minuto por usuario"
    )
    
    # Configuración de Pydantic Settings
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    @property
    def is_production(self) -> bool:
        """Verifica si estamos en producción."""
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def cors_origins(self) -> List[str]:
        """Retorna la lista de orígenes permitidos para CORS."""
        if isinstance(self.ALLOWED_ORIGINS, str):
            return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
        return self.ALLOWED_ORIGINS


# Instancia global de configuración
settings = Settings()