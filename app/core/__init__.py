

"""
Módulo core de la aplicación Comercializadora Digital.

Contiene componentes fundamentales como middlewares, excepciones personalizadas
y utilidades compartidas por toda la aplicación.
"""

from app.core.exceptions import (
    ComercializadoraException,
    BadRequestException,
    UnauthorizedException,
    ForbiddenException,
    NotFoundException,
    ConflictException,
    ValidationException,
    TooManyRequestsException,
    InternalServerErrorException,
    ServiceUnavailableException,
    StorefrontException,
    StorefrontNotFoundError,
    StorefrontNotActiveError,
    StorefrontMaintenanceModeError,
    SupplierException,
    SupplierNotFoundError,
    SupplierNotActiveError,
    RepositoryException,
    DatabaseException,
    DatabaseConnectionError,
    ValidationError,
    http_exception_to_dict,
)

from app.core.middleware import (
    StorefrontMiddleware,
    RequestLoggingMiddleware,
    ErrorHandlingMiddleware,
)

__all__ = [
    # Excepciones
    "ComercializadoraException",
    "BadRequestException",
    "UnauthorizedException",
    "ForbiddenException",
    "NotFoundException",
    "ConflictException",
    "ValidationException",
    "TooManyRequestsException",
    "InternalServerErrorException",
    "ServiceUnavailableException",
    "StorefrontException",
    "StorefrontNotFoundError",
    "StorefrontNotActiveError",
    "StorefrontMaintenanceModeError",
    "SupplierException",
    "SupplierNotFoundError",
    "SupplierNotActiveError",
    "RepositoryException",
    "DatabaseException",
    "DatabaseConnectionError",
    "ValidationError",
    "http_exception_to_dict",
    
    # Middleware
    "StorefrontMiddleware",
    "RequestLoggingMiddleware",
    "ErrorHandlingMiddleware",
]

