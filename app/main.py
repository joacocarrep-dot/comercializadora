
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging
from contextlib import asynccontextmanager

from app.core.exceptions import (
    BadRequestException,
    UnauthorizedException,
    ForbiddenException,
    NotFoundException,
    ConflictException,
    ValidationException,
    TooManyRequestsException,
    InternalServerErrorException,
    ServiceUnavailableException,
    http_exception_to_dict,
)
from app.core.middleware import (
    StorefrontMiddleware,
    RequestLoggingMiddleware,
    ErrorHandlingMiddleware,
)

# Configuración básica de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Lifespan events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up Comercializadora Digital Backend")
    yield
    # Shutdown
    logger.info("Shutting down Comercializadora Digital Backend")

# Crear aplicación FastAPI
app = FastAPI(
    title="Comercializadora Digital API",
    description="Backend para la comercializadora digital - Sistema intermediario entre proveedores y clientes",
    version="1.0.0",
    contact={
        "name": "Equipo de Desarrollo",
        "email": "dev@comercializadora.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan,
)

# Configurar CORS
# En desarrollo permitimos todos los orígenes, en producción se debe restringir
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambiar en producción a los dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Agregar middlewares personalizados
# El orden es importante: primero los que procesan la request, luego los que manejan errores
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(StorefrontMiddleware)

# ============================================================================
# Exception handlers globales
# ============================================================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handler para errores de validación de Pydantic/FastAPI.
    """
    logger.warning(f"Validation error: {exc.errors()}", extra={
        "path": request.url.path,
        "method": request.method,
        "errors": exc.errors(),
    })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "message": "Validation Error",
            "code": "VALIDATION_ERROR",
            "errors": exc.errors(),
            "details": {
                "path": request.url.path,
                "method": request.method,
            }
        }
    )


@app.exception_handler(UnauthorizedException)
async def unauthorized_exception_handler(request: Request, exc: UnauthorizedException):
    """
    Handler para errores 401 Unauthorized.
    """
    logger.warning(f"Unauthorized access: {exc.detail.get('message', '')}", extra={
        "path": request.url.path,
        "method": request.method,
        "details": exc.detail.get('details', {}),
    })
    
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail
    )


@app.exception_handler(ForbiddenException)
async def forbidden_exception_handler(request: Request, exc: ForbiddenException):
    """
    Handler para errores 403 Forbidden.
    """
    logger.warning(f"Forbidden access: {exc.detail.get('message', '')}", extra={
        "path": request.url.path,
        "method": request.method,
        "details": exc.detail.get('details', {}),
    })
    
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail
    )


@app.exception_handler(NotFoundException)
async def not_found_exception_handler(request: Request, exc: NotFoundException):
    """
    Handler para errores 404 Not Found.
    """
    logger.info(f"Resource not found: {exc.detail.get('message', '')}", extra={
        "path": request.url.path,
        "method": request.method,
        "details": exc.detail.get('details', {}),
    })
    
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail
    )


@app.exception_handler(ValidationException)
async def custom_validation_exception_handler(request: Request, exc: ValidationException):
    """
    Handler para errores de validación personalizados (422).
    """
    logger.warning(f"Custom validation error: {exc.detail.get('message', '')}", extra={
        "path": request.url.path,
        "method": request.method,
        "errors": exc.detail.get('errors', {}),
    })
    
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail
    )


@app.exception_handler(ConflictException)
async def conflict_exception_handler(request: Request, exc: ConflictException):
    """
    Handler para errores 409 Conflict.
    """
    logger.warning(f"Conflict error: {exc.detail.get('message', '')}", extra={
        "path": request.url.path,
        "method": request.method,
        "details": exc.detail.get('details', {}),
    })
    
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail
    )


@app.exception_handler(TooManyRequestsException)
async def too_many_requests_exception_handler(request: Request, exc: TooManyRequestsException):
    """
    Handler para errores 429 Too Many Requests.
    """
    logger.warning(f"Rate limit exceeded: {exc.detail.get('message', '')}", extra={
        "path": request.url.path,
        "method": request.method,
        "details": exc.detail.get('details', {}),
    })
    
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Handler global para excepciones no manejadas.
    """
    # Obtener request ID si existe
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    # Log del error con información completa
    logger.error(
        f"Unhandled exception: {str(exc)}",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method,
            "client_host": request.client.host if request.client else "unknown",
            "exception_type": type(exc).__name__,
        },
        exc_info=True
    )
    
    # Si es una excepción HTTP de FastAPI, usar su formato
    from fastapi import HTTPException
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=http_exception_to_dict(exc)
        )
    
    # Para otras excepciones, retornar error 500 genérico
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "message": "Internal Server Error",
            "code": "INTERNAL_SERVER_ERROR",
            "details": {
                "request_id": request_id,
                "error": str(exc) if str(exc) else "Unknown error",
            }
        }
    )


# ============================================================================
# Endpoints principales
# ============================================================================

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint para verificar que la API está funcionando.
    """
    return {
        "status": "healthy",
        "service": "comercializadora-backend",
        "version": "1.0.0"
    }

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Endpoint raíz de la API.
    """
    return {
        "message": "Bienvenido a la API de Comercializadora Digital",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health"
    }

# Importar routers futuros aquí
# from app.api.v1 import suppliers, storefronts, products, etc.

# Importar endpoints de prueba para verificar el middleware core
from app.api.v1.test_endpoints import router as test_router
from app.config.settings import settings

# Montar router de pruebas bajo el prefijo de API
app.include_router(test_router, prefix=settings.API_PREFIX)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,  # Hot-reload para desarrollo
        log_level="info"
    )
