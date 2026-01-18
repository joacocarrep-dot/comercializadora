



"""
Esquemas Pydantic para el modelo Storefront.

Define los esquemas de entrada y salida para las operaciones CRUD de tiendas virtuales.
"""

import secrets
import string
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator, HttpUrl


# ---------- Esquemas Base ----------

class StorefrontBase(BaseModel):
    """Esquema base para Storefront."""
    
    code: str = Field(..., min_length=2, max_length=50, description="Código único de la tienda")
    name: str = Field(..., min_length=2, max_length=255, description="Nombre de la tienda")
    description: Optional[str] = Field(None, description="Descripción de la tienda")
    
    domain: Optional[str] = Field(None, max_length=255, description="Dominio de la tienda")
    base_url: Optional[str] = Field(None, max_length=500, description="URL base de la tienda")
    
    is_active: bool = Field(True, description="Indica si la tienda está activa")
    is_public: bool = Field(False, description="Indica si la tienda es pública")
    maintenance_mode: bool = Field(False, description="Modo mantenimiento activo")
    
    categories: Optional[List[str]] = Field(None, description="Categorías de productos de la tienda")
    tags: Optional[List[str]] = Field(None, description="Etiquetas de la tienda")
    
    contact_email: Optional[str] = Field(None, max_length=255, description="Email de contacto")
    contact_phone: Optional[str] = Field(None, max_length=50, description="Teléfono de contacto")
    support_email: Optional[str] = Field(None, max_length=255, description="Email de soporte")
    
    config: Optional[Dict[str, Any]] = Field(None, description="Configuración general de la tienda")
    payment_config: Optional[Dict[str, Any]] = Field(None, description="Configuración de pagos")
    ai_config: Optional[Dict[str, Any]] = Field(None, description="Configuración de IA")
    notification_config: Optional[Dict[str, Any]] = Field(None, description="Configuración de notificaciones")
    extra_metadata: Optional[Dict[str, Any]] = Field(None, description="Metadatos adicionales de la tienda")
    
    @validator('code')
    def validate_code(cls, v):
        """Valida que el código solo contenga caracteres alfanuméricos, guiones y guiones bajos."""
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('El código solo puede contener letras, números, guiones y guiones bajos')
        return v.lower()
    
    @validator('domain')
    def validate_domain(cls, v):
        """Valida el formato del dominio si se proporciona."""
        if v is None or v == "":
            return v
        
        import re
        # Validación básica de dominio
        domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z]{2,})+$'
        if not re.match(domain_pattern, v):
            raise ValueError('Formato de dominio inválido')
        return v.lower()
    
    @validator('contact_email', 'support_email')
    def validate_email(cls, v):
        """Valida el formato del email si se proporciona."""
        if v is None or v == "":
            return v
        
        from email_validator import validate_email, EmailNotValidError
        try:
            valid = validate_email(v)
            return valid.email
        except EmailNotValidError:
            raise ValueError('Email inválido')


# ---------- Esquemas de Creación ----------

class StorefrontCreate(StorefrontBase):
    """
    Esquema para crear una nueva tienda.
    
    Nota: Los campos sensibles como api_key, api_secret, webhook_secret
    se generan automáticamente o se manejan en endpoints separados por seguridad.
    """
    
    # Campos opcionales para configuración inicial
    api_key: Optional[str] = Field(None, description="API Key personalizada (si no se proporciona, se genera)")
    webhook_url: Optional[str] = Field(None, max_length=500, description="URL para webhooks")
    
    class Config:
        schema_extra = {
            "example": {
                "code": "tienda-ejemplo",
                "name": "Tienda Ejemplo S.A.",
                "description": "Una tienda de ejemplo para demostración",
                "domain": "tienda-ejemplo.com",
                "base_url": "https://tienda-ejemplo.com",
                "is_active": True,
                "is_public": True,
                "maintenance_mode": False,
                "categories": ["electronica", "hogar"],
                "tags": ["premium", "nuevo"],
                "contact_email": "contacto@tienda-ejemplo.com",
                "contact_phone": "+5491133445566",
                "support_email": "soporte@tienda-ejemplo.com",
                "config": {
                    "theme": "light",
                    "currency": "ARS",
                    "language": "es"
                },
                "payment_config": {
                    "mercadopago": {
                        "public_key": "TEST-PUBLIC-KEY"
                    }
                }
            }
        }


# ---------- Esquemas de Actualización ----------

class StorefrontUpdate(BaseModel):
    """
    Esquema para actualizar una tienda existente.
    
    Todos los campos son opcionales.
    """
    
    code: Optional[str] = Field(None, min_length=2, max_length=50, description="Código único de la tienda")
    name: Optional[str] = Field(None, min_length=2, max_length=255, description="Nombre de la tienda")
    description: Optional[str] = Field(None, description="Descripción de la tienda")
    
    domain: Optional[str] = Field(None, max_length=255, description="Dominio de la tienda")
    base_url: Optional[str] = Field(None, max_length=500, description="URL base de la tienda")
    
    is_active: Optional[bool] = Field(None, description="Indica si la tienda está activa")
    is_public: Optional[bool] = Field(None, description="Indica si la tienda es pública")
    maintenance_mode: Optional[bool] = Field(None, description="Modo mantenimiento activo")
    
    categories: Optional[List[str]] = Field(None, description="Categorías de productos de la tienda")
    tags: Optional[List[str]] = Field(None, description="Etiquetas de la tienda")
    
    contact_email: Optional[str] = Field(None, max_length=255, description="Email de contacto")
    contact_phone: Optional[str] = Field(None, max_length=50, description="Teléfono de contacto")
    support_email: Optional[str] = Field(None, max_length=255, description="Email de soporte")
    
    config: Optional[Dict[str, Any]] = Field(None, description="Configuración general de la tienda")
    payment_config: Optional[Dict[str, Any]] = Field(None, description="Configuración de pagos")
    ai_config: Optional[Dict[str, Any]] = Field(None, description="Configuración de IA")
    notification_config: Optional[Dict[str, Any]] = Field(None, description="Configuración de notificaciones")
    extra_metadata: Optional[Dict[str, Any]] = Field(None, description="Metadatos adicionales de la tienda")
    
    # Campos de configuración avanzada
    webhook_url: Optional[str] = Field(None, max_length=500, description="URL para webhooks")
    
    @validator('code')
    def validate_code(cls, v):
        """Valida que el código solo contenga caracteres alfanuméricos, guiones y guiones bajos."""
        if v is None:
            return v
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('El código solo puede contener letras, números, guiones y guiones bajos')
        return v.lower()
    
    @validator('domain')
    def validate_domain(cls, v):
        """Valida el formato del dominio si se proporciona."""
        if v is None or v == "":
            return v
        
        import re
        domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z]{2,})+$'
        if not re.match(domain_pattern, v):
            raise ValueError('Formato de dominio inválido')
        return v.lower()
    
    @validator('contact_email', 'support_email')
    def validate_email(cls, v):
        """Valida el formato del email si se proporciona."""
        if v is None or v == "":
            return v
        
        from email_validator import validate_email, EmailNotValidError
        try:
            valid = validate_email(v)
            return valid.email
        except EmailNotValidError:
            raise ValueError('Email inválido')
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Tienda Ejemplo S.A. (Actualizada)",
                "is_active": False,
                "maintenance_mode": True,
                "config": {
                    "theme": "dark",
                    "currency": "USD"
                }
            }
        }


# ---------- Esquemas de Respuesta ----------

class StorefrontResponse(StorefrontBase):
    """
    Esquema para la respuesta de una tienda.
    
    Incluye todos los campos del modelo excepto información sensible.
    """
    
    id: int = Field(..., description="ID único de la tienda")
    webhook_url: Optional[str] = Field(None, description="URL para webhooks")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Fecha de última actualización")
    
    # Campos calculados o derivados
    api_key_exists: bool = Field(..., description="Indica si la tienda tiene API Key configurada")
    
    class Config:
        from_attributes = True  # Anteriormente orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "code": "tienda-ejemplo",
                "name": "Tienda Ejemplo S.A.",
                "description": "Una tienda de ejemplo para demostración",
                "domain": "tienda-ejemplo.com",
                "base_url": "https://tienda-ejemplo.com",
                "is_active": True,
                "is_public": True,
                "maintenance_mode": False,
                "categories": ["electronica", "hogar"],
                "tags": ["premium", "nuevo"],
                "contact_email": "contacto@tienda-ejemplo.com",
                "contact_phone": "+5491133445566",
                "support_email": "soporte@tienda-ejemplo.com",
                "config": {
                    "theme": "light",
                    "currency": "ARS",
                    "language": "es"
                },
                "payment_config": {
                    "mercadopago": {
                        "public_key": "TEST-PUBLIC-KEY"
                    }
                },
                "webhook_url": "https://tienda-ejemplo.com/webhooks",
                "api_key_exists": True,
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-10T14:30:00Z"
            }
        }


class StorefrontListResponse(BaseModel):
    """
    Esquema para la respuesta de lista de tiendas.
    """
    
    items: List[StorefrontResponse] = Field(..., description="Lista de tiendas")
    total: int = Field(..., description="Número total de tiendas")
    page: int = Field(..., description="Página actual")
    page_size: int = Field(..., description="Tamaño de página")
    total_pages: int = Field(..., description="Número total de páginas")
    
    class Config:
        from_attributes = True


# ---------- Esquemas para Credenciales y API ----------

class StorefrontCredentials(BaseModel):
    """
    Esquema para manejar credenciales de API de una tienda.
    """
    
    api_key: Optional[str] = Field(None, description="API Key para integraciones")
    api_secret: Optional[str] = Field(None, description="API Secret para integraciones")
    webhook_secret: Optional[str] = Field(None, description="Secreto para validar webhooks")
    
    class Config:
        schema_extra = {
            "example": {
                "api_key": "sf_1234567890abcdef",
                "api_secret": "sf_secret_0987654321fedcba",
                "webhook_secret": "wh_secret_abcdef1234567890"
            }
        }


class StorefrontAPIKeyGenerate(BaseModel):
    """
    Esquema para solicitar la generación de una nueva API Key.
    """
    
    key_name: Optional[str] = Field(None, description="Nombre descriptivo para la API Key")
    expires_in_days: Optional[int] = Field(None, ge=1, le=365, description="Días hasta la expiración")
    
    class Config:
        schema_extra = {
            "example": {
                "key_name": "Clave para integración con ERP",
                "expires_in_days": 90
            }
        }


class StorefrontAPIKeyResponse(BaseModel):
    """
    Esquema para la respuesta de generación de API Key.
    
    Nota: La API Key solo se muestra una vez después de generarla.
    """
    
    api_key: str = Field(..., description="API Key generada")
    api_key_id: str = Field(..., description="ID interno de la API Key")
    key_name: Optional[str] = Field(None, description="Nombre descriptivo de la API Key")
    expires_at: Optional[datetime] = Field(None, description="Fecha de expiración")
    created_at: datetime = Field(..., description="Fecha de creación")
    
    class Config:
        schema_extra = {
            "example": {
                "api_key": "sf_live_1234567890abcdef",
                "api_key_id": "key_123",
                "key_name": "Clave para integración con ERP",
                "expires_at": "2024-04-17T12:00:00Z",
                "created_at": "2024-01-17T12:00:00Z"
            }
        }


# ---------- Esquemas para Búsqueda y Filtros ----------

class StorefrontFilter(BaseModel):
    """
    Esquema para filtrar tiendas en búsquedas.
    """
    
    search: Optional[str] = Field(None, description="Término de búsqueda (nombre, código, dominio, email)")
    is_active: Optional[bool] = Field(None, description="Filtrar por estado activo/inactivo")
    is_public: Optional[bool] = Field(None, description="Filtrar por visibilidad pública/privada")
    maintenance_mode: Optional[bool] = Field(None, description="Filtrar por modo mantenimiento")
    
    class Config:
        schema_extra = {
            "example": {
                "search": "ejemplo",
                "is_active": True,
                "is_public": True
            }
        }


# ---------- Funciones de utilidad ----------

def generate_api_key(length: int = 32) -> str:
    """
    Genera una API Key segura.
    
    Args:
        length: Longitud de la API Key
        
    Returns:
        str: API Key generada
    """
    alphabet = string.ascii_letters + string.digits + "_-"
    return "sf_" + ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_api_secret(length: int = 64) -> str:
    """
    Genera un API Secret seguro.
    
    Args:
        length: Longitud del API Secret
        
    Returns:
        str: API Secret generado
    """
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()_-+="
    return ''.join(secrets.choice(alphabet) for _ in range(length))






