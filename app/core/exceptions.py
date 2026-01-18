

"""
Excepciones personalizadas para la aplicación Comercializadora Digital.

Define excepciones específicas del dominio y excepciones HTTP personalizadas
que pueden ser manejadas por los exception handlers globales.
"""

from typing import Optional, Any, Dict
from fastapi import HTTPException, status


class ComercializadoraException(Exception):
    """Excepción base para todas las excepciones personalizadas de la aplicación."""
    
    def __init__(self, message: str, code: str = "INTERNAL_ERROR", details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)


# ============================================================================
# Excepciones HTTP personalizadas (4xx, 5xx)
# ============================================================================

class BadRequestException(HTTPException):
    """400 Bad Request - La solicitud es incorrecta o mal formada."""
    
    def __init__(self, message: str = "Bad Request", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": message,
                "code": "BAD_REQUEST",
                "details": details or {}
            }
        )


class UnauthorizedException(HTTPException):
    """401 Unauthorized - Falta autenticación o credenciales inválidas."""
    
    def __init__(self, message: str = "Unauthorized", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "message": message,
                "code": "UNAUTHORIZED",
                "details": details or {}
            }
        )


class ForbiddenException(HTTPException):
    """403 Forbidden - No tiene permisos para acceder al recurso."""
    
    def __init__(self, message: str = "Forbidden", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": message,
                "code": "FORBIDDEN",
                "details": details or {}
            }
        )


class NotFoundException(HTTPException):
    """404 Not Found - El recurso solicitado no existe."""
    
    def __init__(self, message: str = "Not Found", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": message,
                "code": "NOT_FOUND",
                "details": details or {}
            }
        )


class ConflictException(HTTPException):
    """409 Conflict - Conflicto con el estado actual del recurso."""
    
    def __init__(self, message: str = "Conflict", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": message,
                "code": "CONFLICT",
                "details": details or {}
            }
        )


class ValidationException(HTTPException):
    """422 Unprocessable Entity - Error de validación de datos."""
    
    def __init__(self, message: str = "Validation Error", errors: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": message,
                "code": "VALIDATION_ERROR",
                "errors": errors or {}
            }
        )


class TooManyRequestsException(HTTPException):
    """429 Too Many Requests - Límite de tasa excedido."""
    
    def __init__(self, message: str = "Too Many Requests", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "message": message,
                "code": "RATE_LIMIT_EXCEEDED",
                "details": details or {}
            }
        )


class InternalServerErrorException(HTTPException):
    """500 Internal Server Error - Error interno del servidor."""
    
    def __init__(self, message: str = "Internal Server Error", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": message,
                "code": "INTERNAL_SERVER_ERROR",
                "details": details or {}
            }
        )


class ServiceUnavailableException(HTTPException):
    """503 Service Unavailable - Servicio temporalmente no disponible."""
    
    def __init__(self, message: str = "Service Unavailable", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "message": message,
                "code": "SERVICE_UNAVAILABLE",
                "details": details or {}
            }
        )


# ============================================================================
# Excepciones de dominio específicas
# ============================================================================

class StorefrontException(ComercializadoraException):
    """Excepción base para errores relacionados con storefronts."""
    
    def __init__(self, message: str, code: str = "STOREFRONT_ERROR", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code, details)


class StorefrontNotFoundError(StorefrontException):
    """Error cuando no se encuentra un storefront."""
    
    def __init__(self, storefront_code: Optional[str] = None, api_key: Optional[str] = None):
        message = "Storefront not found"
        details = {}
        if storefront_code:
            details["storefront_code"] = storefront_code
        if api_key:
            details["api_key"] = f"{api_key[:8]}..." if api_key and len(api_key) > 8 else api_key
        
        super().__init__(message, "STOREFRONT_NOT_FOUND", details)


class StorefrontNotActiveError(StorefrontException):
    """Error cuando un storefront no está activo."""
    
    def __init__(self, storefront_code: str):
        super().__init__(
            message=f"Storefront '{storefront_code}' is not active",
            code="STOREFRONT_NOT_ACTIVE",
            details={"storefront_code": storefront_code}
        )


class StorefrontMaintenanceModeError(StorefrontException):
    """Error cuando un storefront está en modo mantenimiento."""
    
    def __init__(self, storefront_code: str):
        super().__init__(
            message=f"Storefront '{storefront_code}' is in maintenance mode",
            code="STOREFRONT_MAINTENANCE_MODE",
            details={"storefront_code": storefront_code}
        )


class SupplierException(ComercializadoraException):
    """Excepción base para errores relacionados con suppliers."""
    
    def __init__(self, message: str, code: str = "SUPPLIER_ERROR", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code, details)


class SupplierNotFoundError(SupplierException):
    """Error cuando no se encuentra un supplier."""
    
    def __init__(self, supplier_code: Optional[str] = None, supplier_id: Optional[int] = None):
        message = "Supplier not found"
        details = {}
        if supplier_code:
            details["supplier_code"] = supplier_code
        if supplier_id:
            details["supplier_id"] = supplier_id
        
        super().__init__(message, "SUPPLIER_NOT_FOUND", details)


class SupplierNotActiveError(SupplierException):
    """Error cuando un supplier no está activo."""
    
    def __init__(self, supplier_code: str):
        super().__init__(
            message=f"Supplier '{supplier_code}' is not active",
            code="SUPPLIER_NOT_ACTIVE",
            details={"supplier_code": supplier_code}
        )


class RepositoryException(ComercializadoraException):
    """Excepción base para errores en repositorios."""
    
    def __init__(self, message: str, code: str = "REPOSITORY_ERROR", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code, details)


class DatabaseException(ComercializadoraException):
    """Excepción base para errores de base de datos."""
    
    def __init__(self, message: str, code: str = "DATABASE_ERROR", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code, details)


class DatabaseConnectionError(DatabaseException):
    """Error de conexión a la base de datos."""
    
    def __init__(self, message: str = "Database connection error"):
        super().__init__(message, "DATABASE_CONNECTION_ERROR")


class ValidationError(ComercializadoraException):
    """Error de validación de datos."""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Optional[Any] = None):
        details = {}
        if field:
            details["field"] = field
        if value:
            details["value"] = value
        
        super().__init__(message, "VALIDATION_ERROR", details)


# ============================================================================
# Funciones de utilidad para excepciones
# ============================================================================

def http_exception_to_dict(exc: HTTPException) -> Dict[str, Any]:
    """
    Convierte una excepción HTTP a un diccionario estandarizado.
    
    Args:
        exc: Excepción HTTP
        
    Returns:
        Diccionario con la estructura estandarizada de error
    """
    if isinstance(exc.detail, dict):
        return exc.detail
    
    return {
        "message": str(exc.detail) if exc.detail else "Error occurred",
        "code": "HTTP_ERROR",
        "details": {}
    }


