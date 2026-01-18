
"""
Configuración de la aplicación usando Pydantic BaseSettings.
Carga variables de entorno desde el archivo .env
"""
import os
from typing import List, Optional
from pydantic import Field, PostgresDsn, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuración principal de la aplicación"""
    
    # Entorno
    ENVIRONMENT: str = Field("development", description="Entorno: development, staging, production")
    DEBUG: bool = Field(False, description="Modo debug")
    
    # Base de datos
    DATABASE_URL: PostgresDsn = Field(
        "postgresql://comercializadora:comercializadora@localhost:5432/comercializadora",
        description="URL de conexión a PostgreSQL"
    )
    DATABASE_POOL_SIZE: int = Field(5, description="Tamaño del pool de conexiones")
    DATABASE_MAX_OVERFLOW: int = Field(10, description="Máximo overflow del pool")
    
    # Seguridad y autenticación
    SECRET_KEY: str = Field("dev-secret-key-change-in-production", description="Clave secreta para JWT")
    ALGORITHM: str = Field("HS256", description="Algoritmo de encriptación JWT")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, description="Minutos de expiración del token")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(7, description="Días de expiración del refresh token")
    
    # CORS
    ALLOWED_ORIGINS: List[str] = Field(
        ["http://localhost:3000", "http://localhost:5173"],
        description="Orígenes permitidos para CORS"
    )
    ALLOWED_METHODS: List[str] = Field(
        ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        description="Métodos HTTP permitidos"
    )
    ALLOWED_HEADERS: List[str] = Field(
        ["*"], description="Headers permitidos"
    )
    
    # Logging
    LOG_LEVEL: str = Field("INFO", description="Nivel de logging")
    LOG_FORMAT: str = Field(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Formato de logs"
    )
    
    # Integraciones - Pagos
    MERCADOPAGO_ACCESS_TOKEN: Optional[str] = Field(
        None, description="Token de acceso a MercadoPago"
    )
    MERCADOPAGO_PUBLIC_KEY: Optional[str] = Field(
        None, description="Clave pública de MercadoPago"
    )
    
    # Integraciones - IA
    GEMINI_API_KEY: Optional[str] = Field(
        None, description="API Key para Google Gemini"
    )
    
    # Integraciones - Comunicación
    WHATSAPP_API_TOKEN: Optional[str] = Field(
        None, description="Token para API de WhatsApp"
    )
    SENDGRID_API_KEY: Optional[str] = Field(
        None, description="API Key para SendGrid (emails)"
    )
    TWILIO_ACCOUNT_SID: Optional[str] = Field(
        None, description="SID de cuenta Twilio (SMS)"
    )
    TWILIO_AUTH_TOKEN: Optional[str] = Field(
        None, description="Token de autenticación Twilio"
    )
    TWILIO_PHONE_NUMBER: Optional[str] = Field(
        None, description="Número de teléfono Twilio"
    )
    
    # Configuración de la aplicación
    APP_NAME: str = Field("Comercializadora Digital", description="Nombre de la aplicación")
    APP_VERSION: str = Field("1.0.0", description="Versión de la aplicación")
    API_PREFIX: str = Field("/api/v1", description="Prefijo de la API")
    
    # Límites y timeouts
    REQUEST_TIMEOUT: int = Field(30, description="Timeout de solicitudes en segundos")
    MAX_UPLOAD_SIZE: int = Field(10 * 1024 * 1024, description="Tamaño máximo de upload (10MB)")
    
    # Redis (opcional para cache)
    REDIS_URL: Optional[str] = Field(
        None, description="URL de conexión a Redis"
    )
    
    # Validadores
    @validator("ALLOWED_ORIGINS", pre=True)
    def parse_allowed_origins(cls, v):
        """Parse ALLOWED_ORIGINS si viene como string separado por comas"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v
    
    @validator("DATABASE_URL", pre=True)
    def validate_database_url(cls, v):
        """Asegura que DATABASE_URL use asyncpg para conexiones asíncronas"""
        if v and not v.startswith("postgresql+asyncpg://"):
            # Convertir a asyncpg si no lo está
            v = v.replace("postgresql://", "postgresql+asyncpg://")
        return v
    
    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        """Valida que el entorno sea uno de los permitidos"""
        allowed = ["development", "staging", "production", "test"]
        if v not in allowed:
            raise ValueError(f"ENVIRONMENT debe ser uno de: {', '.join(allowed)}")
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignorar variables extra en .env


# Instancia global de configuración
settings = Settings()

# Configuración específica por entorno
def get_settings() -> Settings:
    """
    Retorna la configuración según el entorno.
    Útil para testing o para diferentes configuraciones.
    """
    return Settings()


# Variables derivadas
def is_development() -> bool:
    """Verifica si estamos en entorno de desarrollo"""
    return settings.ENVIRONMENT == "development"


def is_production() -> bool:
    """Verifica si estamos en entorno de producción"""
    return settings.ENVIRONMENT == "production"


def is_staging() -> bool:
    """Verifica si estamos en entorno de staging"""
    return settings.ENVIRONMENT == "staging"


def is_test() -> bool:
    """Verifica si estamos en entorno de testing"""
    return settings.ENVIRONMENT == "test"


# Configuración de logging según entorno
LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": settings.LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": settings.LOG_LEVEL,
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "default",
            "filename": f"logs/{settings.ENVIRONMENT}.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "level": settings.LOG_LEVEL,
        },
    },
    "loggers": {
        "comercializadora": {
            "handlers": ["console", "file"] if is_production() else ["console"],
            "level": settings.LOG_LEVEL,
            "propagate": False,
        },
        "uvicorn": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "sqlalchemy.engine": {
            "handlers": ["console"],
            "level": "WARNING" if is_production() else "INFO",
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
}
