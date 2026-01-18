



"""
Esquemas Pydantic para el modelo Supplier.

Define los esquemas de entrada y salida para las operaciones CRUD de proveedores.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator


# ---------- Esquemas Base ----------

class SupplierBase(BaseModel):
    """Esquema base para Supplier."""
    
    code: str = Field(..., min_length=2, max_length=50, description="Código único del proveedor")
    name: str = Field(..., min_length=2, max_length=255, description="Nombre del proveedor")
    
    contact_name: Optional[str] = Field(None, max_length=255, description="Nombre de contacto")
    contact_email: Optional[str] = Field(None, max_length=255, description="Email de contacto")
    contact_phone: Optional[str] = Field(None, max_length=50, description="Teléfono de contacto")
    website: Optional[str] = Field(None, max_length=255, description="Sitio web del proveedor")
    
    is_active: bool = Field(True, description="Indica si el proveedor está activo")
    sync_enabled: bool = Field(False, description="Indica si la sincronización automática está habilitada")
    sync_frequency: Optional[str] = Field(None, description="Frecuencia de sincronización (daily, hourly, etc.)")
    
    api_endpoint: Optional[str] = Field(None, max_length=500, description="Endpoint base de la API")
    api_config: Optional[Dict[str, Any]] = Field(None, description="Configuración de API en formato JSON")
    extra_metadata: Optional[Dict[str, Any]] = Field(None, description="Metadatos adicionales del proveedor")
    
    @validator('code')
    def validate_code(cls, v):
        """Valida que el código solo contenga caracteres alfanuméricos, guiones y guiones bajos."""
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('El código solo puede contener letras, números, guiones y guiones bajos')
        return v.lower()
    
    @validator('contact_email')
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

class SupplierCreate(SupplierBase):
    """
    Esquema para crear un nuevo proveedor.
    
    Nota: No se incluyen campos sensibles como api_key, api_secret, api_token aquí.
    Estos se manejan en endpoints separados por seguridad.
    """
    
    class Config:
        schema_extra = {
            "example": {
                "code": "proveedor-abc",
                "name": "Proveedor ABC S.A.",
                "contact_name": "Juan Pérez",
                "contact_email": "juan@proveedorabc.com",
                "contact_phone": "+5491133445566",
                "website": "https://proveedorabc.com",
                "is_active": True,
                "sync_enabled": False,
                "sync_frequency": "daily",
                "api_endpoint": "https://api.proveedorabc.com/v1",
                "api_config": {
                    "auth_type": "api_key",
                    "timeout": 30
                }
            }
        }


class SupplierCreateWithCredentials(SupplierCreate):
    """
    Esquema para crear un proveedor incluyendo credenciales de API.
    
    Solo para uso interno o en entornos seguros.
    """
    
    api_key: Optional[str] = Field(None, description="API Key para autenticación")
    api_secret: Optional[str] = Field(None, description="API Secret para autenticación")
    api_token: Optional[str] = Field(None, description="Token de acceso a la API")
    api_token_expires_at: Optional[str] = Field(None, description="Fecha de expiración del token (ISO string)")


# ---------- Esquemas de Actualización ----------

class SupplierUpdate(BaseModel):
    """
    Esquema para actualizar un proveedor existente.
    
    Todos los campos son opcionales.
    """
    
    code: Optional[str] = Field(None, min_length=2, max_length=50, description="Código único del proveedor")
    name: Optional[str] = Field(None, min_length=2, max_length=255, description="Nombre del proveedor")
    
    contact_name: Optional[str] = Field(None, max_length=255, description="Nombre de contacto")
    contact_email: Optional[str] = Field(None, max_length=255, description="Email de contacto")
    contact_phone: Optional[str] = Field(None, max_length=50, description="Teléfono de contacto")
    website: Optional[str] = Field(None, max_length=255, description="Sitio web del proveedor")
    
    is_active: Optional[bool] = Field(None, description="Indica si el proveedor está activo")
    sync_enabled: Optional[bool] = Field(None, description="Indica si la sincronización automática está habilitada")
    sync_frequency: Optional[str] = Field(None, description="Frecuencia de sincronización (daily, hourly, etc.)")
    
    api_endpoint: Optional[str] = Field(None, max_length=500, description="Endpoint base de la API")
    api_config: Optional[Dict[str, Any]] = Field(None, description="Configuración de API en formato JSON")
    extra_metadata: Optional[Dict[str, Any]] = Field(None, description="Metadatos adicionales del proveedor")
    
    # Campos sensibles - solo se actualizan a través de endpoints específicos
    api_key: Optional[str] = Field(None, description="API Key para autenticación")
    api_secret: Optional[str] = Field(None, description="API Secret para autenticación")
    api_token: Optional[str] = Field(None, description="Token de acceso a la API")
    api_token_expires_at: Optional[str] = Field(None, description="Fecha de expiración del token (ISO string)")
    
    @validator('code')
    def validate_code(cls, v):
        """Valida que el código solo contenga caracteres alfanuméricos, guiones y guiones bajos."""
        if v is None:
            return v
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('El código solo puede contener letras, números, guiones y guiones bajos')
        return v.lower()
    
    @validator('contact_email')
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
                "name": "Proveedor ABC S.A. (Actualizado)",
                "contact_email": "nuevo-contacto@proveedorabc.com",
                "is_active": False,
                "sync_enabled": True
            }
        }


# ---------- Esquemas de Respuesta ----------

class SupplierResponse(SupplierBase):
    """
    Esquema para la respuesta de un proveedor.
    
    Incluye todos los campos del modelo excepto información sensible.
    """
    
    id: int = Field(..., description="ID único del proveedor")
    last_sync_at: Optional[str] = Field(None, description="Última fecha de sincronización exitosa (ISO string)")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Fecha de última actualización")
    
    class Config:
        from_attributes = True  # Anteriormente orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "code": "proveedor-abc",
                "name": "Proveedor ABC S.A.",
                "contact_name": "Juan Pérez",
                "contact_email": "juan@proveedorabc.com",
                "contact_phone": "+5491133445566",
                "website": "https://proveedorabc.com",
                "is_active": True,
                "sync_enabled": False,
                "sync_frequency": "daily",
                "api_endpoint": "https://api.proveedorabc.com/v1",
                "api_config": {
                    "auth_type": "api_key",
                    "timeout": 30
                },
                "last_sync_at": "2024-01-15T10:30:00Z",
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-10T14:30:00Z"
            }
        }


class SupplierListResponse(BaseModel):
    """
    Esquema para la respuesta de lista de proveedores.
    """
    
    items: List[SupplierResponse] = Field(..., description="Lista de proveedores")
    total: int = Field(..., description="Número total de proveedores")
    page: int = Field(..., description="Página actual")
    page_size: int = Field(..., description="Tamaño de página")
    total_pages: int = Field(..., description="Número total de páginas")
    
    class Config:
        from_attributes = True


# ---------- Esquemas para Credenciales ----------

class SupplierCredentials(BaseModel):
    """
    Esquema para manejar credenciales de API de un proveedor.
    """
    
    api_key: Optional[str] = Field(None, description="API Key para autenticación")
    api_secret: Optional[str] = Field(None, description="API Secret para autenticación")
    api_token: Optional[str] = Field(None, description="Token de acceso a la API")
    api_token_expires_at: Optional[str] = Field(None, description="Fecha de expiración del token (ISO string)")
    
    class Config:
        schema_extra = {
            "example": {
                "api_key": "ak_1234567890abcdef",
                "api_secret": "as_0987654321fedcba",
                "api_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "api_token_expires_at": "2024-12-31T23:59:59Z"
            }
        }


# ---------- Esquemas para Sincronización ----------

class SupplierSyncRequest(BaseModel):
    """
    Esquema para solicitar una sincronización manual de un proveedor.
    """
    
    force_full_sync: bool = Field(False, description="Forzar sincronización completa (no incremental)")
    
    class Config:
        schema_extra = {
            "example": {
                "force_full_sync": True
            }
        }


class SupplierSyncResponse(BaseModel):
    """
    Esquema para la respuesta de una sincronización.
    """
    
    supplier_id: int = Field(..., description="ID del proveedor")
    sync_type: str = Field(..., description="Tipo de sincronización (full, incremental)")
    status: str = Field(..., description="Estado de la sincronización (success, failed, partial)")
    products_processed: int = Field(0, description="Número de productos procesados")
    products_created: int = Field(0, description="Número de productos creados")
    products_updated: int = Field(0, description="Número de productos actualizados")
    products_skipped: int = Field(0, description="Número de productos omitidos")
    error_message: Optional[str] = Field(None, description="Mensaje de error si la sincronización falló")
    started_at: datetime = Field(..., description="Fecha y hora de inicio")
    completed_at: Optional[datetime] = Field(None, description="Fecha y hora de finalización")
    
    class Config:
        schema_extra = {
            "example": {
                "supplier_id": 1,
                "sync_type": "full",
                "status": "success",
                "products_processed": 150,
                "products_created": 25,
                "products_updated": 125,
                "products_skipped": 0,
                "started_at": "2024-01-17T10:00:00Z",
                "completed_at": "2024-01-17T10:05:30Z"
            }
        }


# ---------- Esquemas para Búsqueda y Filtros ----------

class SupplierFilter(BaseModel):
    """
    Esquema para filtrar proveedores en búsquedas.
    """
    
    search: Optional[str] = Field(None, description="Término de búsqueda (nombre, código, email)")
    is_active: Optional[bool] = Field(None, description="Filtrar por estado activo/inactivo")
    sync_enabled: Optional[bool] = Field(None, description="Filtrar por sincronización habilitada")
    
    class Config:
        schema_extra = {
            "example": {
                "search": "ABC",
                "is_active": True,
                "sync_enabled": False
            }
        }




