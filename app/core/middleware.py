


"""
Middleware para la aplicación Comercializadora Digital.

Incluye:
1. StorefrontMiddleware - Identificación de tienda por API Key
2. RequestLoggingMiddleware - Logging de solicitudes HTTP
3. ErrorHandlingMiddleware - Manejo centralizado de errores
"""

import time
import uuid
import logging
from typing import Callable, Optional
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.exceptions import (
    UnauthorizedException,
    StorefrontNotFoundError,
    StorefrontNotActiveError,
    StorefrontMaintenanceModeError
)
from app.db.session import session_manager
from app.repositories.storefront_repo import StorefrontRepository

# Configurar logger
logger = logging.getLogger(__name__)


class StorefrontMiddleware(BaseHTTPMiddleware):
    """
    Middleware para identificar storefronts mediante API Key.
    
    Extrae la API Key del header `X-API-Key` y busca el storefront correspondiente
    en la base de datos. Inyecta el storefront en `request.state.storefront`.
    
    Si no se proporciona API Key o es inválida, retorna 401 Unauthorized.
    """
    
    def __init__(
        self,
        app: FastAPI,
        exempt_paths: Optional[list[str]] = None
    ):
        super().__init__(app)
        self.exempt_paths = exempt_paths or [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
            "/"
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Procesa cada solicitud para identificar el storefront.
        
        Args:
            request: Solicitud HTTP
            call_next: Función para continuar con el siguiente middleware/handler
            
        Returns:
            Response: Respuesta HTTP
        """
        # Verificar si la ruta está exenta
        if any(request.url.path.startswith(path) for path in self.exempt_paths):
            return await call_next(request)
        
        # Extraer API Key del header
        api_key = request.headers.get("X-API-Key")
        
        if not api_key:
            raise UnauthorizedException(
                message="API Key required",
                details={"header": "X-API-Key"}
            )
        
        # Buscar storefront en la base de datos
        try:
            async with session_manager.get_session() as session:
                storefront_repo = StorefrontRepository(session)
                storefront = await storefront_repo.get_by_code(api_key)
                
                if not storefront:
                    raise StorefrontNotFoundError(api_key=api_key)
                
                # Verificar si el storefront está activo
                if not storefront.is_active:
                    raise StorefrontNotActiveError(storefront.code)
                
                # Verificar si está en modo mantenimiento
                if storefront.maintenance_mode:
                    raise StorefrontMaintenanceModeError(storefront.code)
                
                # Inyectar storefront en request.state
                request.state.storefront = storefront
                request.state.storefront_id = storefront.id
                request.state.storefront_code = storefront.code
                
                # Continuar con la solicitud
                return await call_next(request)
                
        except (StorefrontNotFoundError, StorefrontNotActiveError, 
                StorefrontMaintenanceModeError) as e:
            # Convertir excepciones de dominio a HTTP
            raise UnauthorizedException(
                message=str(e.message),
                details=e.details
            )
        except Exception as e:
            # Error interno
            logger.error(f"Error in StorefrontMiddleware: {str(e)}", exc_info=True)
            raise UnauthorizedException(
                message="Internal authentication error",
                details={"error": str(e)}
            )


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware para logging de solicitudes HTTP.
    
    Registra:
    - Método HTTP, ruta, código de estado
    - Duración de la solicitud
    - Request ID único para correlación
    """
    
    def __init__(self, app: FastAPI):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Procesa cada solicitud para logging.
        
        Args:
            request: Solicitud HTTP
            call_next: Función para continuar con el siguiente middleware/handler
            
        Returns:
            Response: Respuesta HTTP
        """
        # Generar request ID único
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Registrar inicio de la solicitud
        start_time = time.time()
        
        # Headers de logging
        log_headers = {
            "X-Request-ID": request_id,
            "User-Agent": request.headers.get("User-Agent", "Unknown"),
            "X-Forwarded-For": request.headers.get("X-Forwarded-For", ""),
            "X-API-Key": request.headers.get("X-API-Key", ""),
        }
        
        # Log de solicitud entrante
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "headers": log_headers,
                "client_host": request.client.host if request.client else "unknown",
            }
        )
        
        try:
            # Procesar solicitud
            response = await call_next(request)
            
            # Calcular duración
            duration = time.time() - start_time
            
            # Log de respuesta
            logger.info(
                f"Request completed: {request.method} {request.url.path} {response.status_code}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": round(duration * 1000, 2),
                    "response_headers": dict(response.headers),
                }
            )
            
            # Agregar request ID a los headers de respuesta
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{duration:.3f}s"
            
            return response
            
        except Exception as e:
            # Calcular duración incluso en caso de error
            duration = time.time() - start_time
            
            # Log de error
            logger.error(
                f"Request failed: {request.method} {request.url.path} - {str(e)}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "error": str(e),
                    "duration_ms": round(duration * 1000, 2),
                    "exception_type": type(e).__name__,
                },
                exc_info=True
            )
            
            # Re-lanzar la excepción para que la manejen los exception handlers
            raise


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Middleware para manejo centralizado de errores.
    
    Captura excepciones no manejadas y las convierte en respuestas JSON estandarizadas.
    """
    
    def __init__(self, app: FastAPI):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Procesa cada solicitud y maneja errores no capturados.
        
        Args:
            request: Solicitud HTTP
            call_next: Función para continuar con el siguiente middleware/handler
            
        Returns:
            Response: Respuesta HTTP
        """
        try:
            return await call_next(request)
            
        except Exception as e:
            # Log del error
            logger.error(
                f"Unhandled exception in request: {request.method} {request.url.path}",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "error": str(e),
                    "exception_type": type(e).__name__,
                },
                exc_info=True
            )
            
            # Si ya es una excepción HTTP de FastAPI, la dejamos pasar
            # (será manejada por los exception handlers de FastAPI)
            from fastapi import HTTPException
            if isinstance(e, HTTPException):
                raise
            
            # Para otras excepciones, retornamos error 500
            return JSONResponse(
                status_code=500,
                content={
                    "message": "Internal Server Error",
                    "code": "INTERNAL_SERVER_ERROR",
                    "details": {
                        "error": str(e),
                        "request_id": getattr(request.state, "request_id", "unknown")
                    }
                }
            )



