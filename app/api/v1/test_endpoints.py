

"""
Endpoints de prueba para verificar el funcionamiento del middleware core.
"""

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    BadRequestException,
    UnauthorizedException,
    NotFoundException,
    ValidationException,
    InternalServerErrorException,
)
from app.db.session import get_session

router = APIRouter(prefix="/test", tags=["Test"])


@router.get("/health")
async def test_health():
    """
    Endpoint de prueba básico sin autenticación.
    """
    return {
        "status": "ok",
        "message": "Middleware core está funcionando",
        "timestamp": "2024-01-17T00:00:00Z"
    }


@router.get("/storefront")
async def test_storefront_middleware(request: Request):
    """
    Endpoint que demuestra el funcionamiento del StorefrontMiddleware.
    
    Requiere header: X-API-Key: <storefront_api_key>
    """
    # Verificar que el storefront fue inyectado por el middleware
    if not hasattr(request.state, 'storefront'):
        raise UnauthorizedException(
            message="StorefrontMiddleware no inyectó storefront en request.state",
            details={"header_required": "X-API-Key"}
        )
    
    storefront = request.state.storefront
    
    return {
        "message": "Storefront identificado correctamente",
        "storefront": {
            "id": storefront.id,
            "code": storefront.code,
            "name": getattr(storefront, 'name', 'N/A'),
            "is_active": storefront.is_active,
            "maintenance_mode": getattr(storefront, 'maintenance_mode', False),
        },
        "request_id": getattr(request.state, 'request_id', 'N/A'),
    }


@router.get("/logging")
async def test_logging_middleware(request: Request):
    """
    Endpoint que demuestra el funcionamiento del RequestLoggingMiddleware.
    
    Muestra el request ID único generado para cada solicitud.
    """
    request_id = getattr(request.state, 'request_id', 'no_request_id')
    
    return {
        "message": "RequestLoggingMiddleware está funcionando",
        "request_id": request_id,
        "headers": {
            "user_agent": request.headers.get("User-Agent"),
            "client_host": request.client.host if request.client else "unknown",
        },
        "note": "Revisa los logs para ver la entrada de logging completa"
    }


@router.get("/errors/{error_type}")
async def test_error_handling(
    error_type: str,
    request: Request,
    session: AsyncSession = Depends(get_session)
):
    """
    Endpoint para probar los exception handlers globales.
    
    Tipos de error disponibles:
    - bad_request: 400 Bad Request
    - unauthorized: 401 Unauthorized
    - not_found: 404 Not Found
    - validation: 422 Validation Error
    - internal: 500 Internal Server Error
    - database: Simula error de base de datos
    """
    
    error_type = error_type.lower()
    
    if error_type == "bad_request":
        raise BadRequestException(
            message="Este es un error 400 de prueba",
            details={
                "test_field": "valor de prueba",
                "request_path": request.url.path,
            }
        )
    
    elif error_type == "unauthorized":
        raise UnauthorizedException(
            message="No autorizado para acceder a este recurso",
            details={
                "required_scopes": ["read:test", "write:test"],
                "provided_scopes": ["read:public"],
            }
        )
    
    elif error_type == "not_found":
        raise NotFoundException(
            resource_type="TestResource",
            resource_id="test-123",
            details={
                "searched_in": ["test_database", "cache"],
                "suggestions": ["Verificar ID", "Crear recurso primero"]
            }
        )
    
    elif error_type == "validation":
        raise ValidationException(
            message="Error de validación en campos de entrada",
            errors={
                "email": ["Debe ser un email válido"],
                "password": [
                    "Debe tener al menos 8 caracteres",
                    "Debe contener al menos un número"
                ]
            }
        )
    
    elif error_type == "internal":
        raise InternalServerErrorException(
            message="Error interno del servidor simulado",
            details={
                "component": "test_service",
                "operation": "simulate_failure",
                "trace_id": getattr(request.state, 'request_id', 'unknown')
            }
        )
    
    elif error_type == "database":
        # Simular error de base de datos
        try:
            # Intentar una operación que fallará
            await session.execute("SELECT * FROM non_existent_table")
        except Exception as e:
            # Este error será manejado por el global_exception_handler
            raise Exception(f"Error de base de datos simulado: {str(e)}")
    
    else:
        raise BadRequestException(
            message=f"Tipo de error no soportado: {error_type}",
            details={
                "supported_error_types": [
                    "bad_request", "unauthorized", "not_found",
                    "validation", "internal", "database"
                ]
            }
        )


@router.get("/protected")
async def test_protected_endpoint(request: Request):
    """
    Endpoint protegido que requiere API Key.
    
    Demuestra la integración completa del middleware.
    """
    # Verificar que todos los middlewares funcionaron
    checks = {
        "storefront_middleware": hasattr(request.state, 'storefront'),
        "logging_middleware": hasattr(request.state, 'request_id'),
        "storefront_active": False,
        "storefront_not_maintenance": False,
    }
    
    if checks["storefront_middleware"]:
        storefront = request.state.storefront
        checks["storefront_active"] = storefront.is_active
        checks["storefront_not_maintenance"] = not getattr(storefront, 'maintenance_mode', False)
    
    return {
        "message": "Endpoint protegido accedido exitosamente",
        "middleware_checks": checks,
        "request_info": {
            "id": getattr(request.state, 'request_id', 'N/A'),
            "method": request.method,
            "path": request.url.path,
            "storefront_id": getattr(request.state, 'storefront_id', 'N/A'),
            "storefront_code": getattr(request.state, 'storefront_code', 'N/A'),
        },
        "timestamp": "2024-01-17T00:00:00Z"
    }


