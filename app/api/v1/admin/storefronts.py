



"""
Endpoints CRUD para la administración de tiendas virtuales (Storefronts).

Requiere autenticación de administrador.
"""

import secrets
import string
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import require_admin
from app.db.session import get_session
from app.models.user import User
from app.repositories.storefront_repo import StorefrontRepository
from app.schemas.storefront import (
    StorefrontCreate,
    StorefrontUpdate,
    StorefrontResponse,
    StorefrontListResponse,
    StorefrontAPIKeyGenerate,
    StorefrontAPIKeyResponse,
    generate_api_key,
    generate_api_secret,
)

router = APIRouter(prefix="/admin/storefronts", tags=["Admin - Storefronts"])


# ---------- Funciones auxiliares ----------

def generate_storefront_api_key() -> str:
    """
    Genera una API Key segura para storefronts.
    
    Returns:
        str: API Key generada con prefijo 'sf_'
    """
    alphabet = string.ascii_letters + string.digits + "_-"
    return "sf_" + ''.join(secrets.choice(alphabet) for _ in range(32))


def generate_webhook_secret() -> str:
    """
    Genera un secreto seguro para webhooks.
    
    Returns:
        str: Secreto generado
    """
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()_-+="
    return ''.join(secrets.choice(alphabet) for _ in range(64))


# ---------- Endpoints CRUD ----------

@router.post(
    "/",
    response_model=StorefrontResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva tienda",
    description="Crea una nueva tienda virtual. Genera automáticamente API Key si no se proporciona."
)
async def create_storefront(
    storefront_data: StorefrontCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin)
) -> StorefrontResponse:
    """
    Crea una nueva tienda virtual.
    
    Args:
        storefront_data: Datos de la tienda a crear
        session: Sesión de base de datos
        current_user: Usuario administrador autenticado
        
    Returns:
        StorefrontResponse: Tienda creada
    """
    storefront_repo = StorefrontRepository(session)
    
    # Verificar que el código no exista
    existing_by_code = await storefront_repo.get_by_code(storefront_data.code)
    if existing_by_code:
        from app.core.exceptions import ConflictException
        raise ConflictException(
            resource_type="Storefront",
            resource_id=storefront_data.code,
            details={"field": "code", "value": storefront_data.code}
        )
    
    # Verificar que el dominio no exista (si se proporciona)
    if storefront_data.domain:
        existing_by_domain = await storefront_repo.get_by_domain(storefront_data.domain)
        if existing_by_domain:
            from app.core.exceptions import ConflictException
            raise ConflictException(
                resource_type="Storefront",
                resource_id=storefront_data.domain,
                details={"field": "domain", "value": storefront_data.domain}
            )
    
    # Preparar datos para creación
    storefront_dict = storefront_data.model_dump(exclude_unset=True)
    
    # Generar API Key automáticamente si no se proporcionó
    if not storefront_dict.get('api_key'):
        storefront_dict['api_key'] = generate_storefront_api_key()
        # También generar API Secret
        storefront_dict['api_secret'] = generate_api_secret()
    
    # Generar webhook secret si hay webhook URL
    if storefront_dict.get('webhook_url') and not storefront_dict.get('webhook_secret'):
        storefront_dict['webhook_secret'] = generate_webhook_secret()
    
    # Crear tienda
    storefront = await storefront_repo.create(storefront_dict)
    
    # Convertir a respuesta
    return StorefrontResponse(
        **storefront.to_dict(),
        api_key_exists=bool(storefront.api_key)
    )


@router.get(
    "/",
    response_model=StorefrontListResponse,
    summary="Listar tiendas",
    description="Obtiene una lista paginada de tiendas virtuales. Filtros opcionales."
)
async def list_storefronts(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(20, ge=1, le=100, description="Tamaño de página"),
    search: Optional[str] = Query(None, description="Término de búsqueda (nombre, código, dominio, email)"),
    is_active: Optional[bool] = Query(None, description="Filtrar por estado activo/inactivo"),
    is_public: Optional[bool] = Query(None, description="Filtrar por visibilidad pública/privada"),
    maintenance_mode: Optional[bool] = Query(None, description="Filtrar por modo mantenimiento"),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin)
) -> StorefrontListResponse:
    """
    Lista tiendas con paginación y filtros.
    
    Args:
        page: Número de página
        page_size: Tamaño de página
        search: Término de búsqueda
        is_active: Filtrar por estado activo
        is_public: Filtrar por visibilidad pública
        maintenance_mode: Filtrar por modo mantenimiento
        session: Sesión de base de datos
        current_user: Usuario administrador autenticado
        
    Returns:
        StorefrontListResponse: Lista paginada de tiendas
    """
    storefront_repo = StorefrontRepository(session)
    
    # Calcular offset
    offset = (page - 1) * page_size
    
    # Determinar qué tiendas obtener
    if is_active is not None and is_active is True:
        # Solo activas
        storefronts = await storefront_repo.get_active_storefronts()
    else:
        # Buscar con filtros
        storefronts = await storefront_repo.search(
            search_term=search,
            skip=offset,
            limit=page_size,
            only_active=is_active if is_active is not None else None
        )
    
    # Aplicar filtros adicionales manualmente
    filtered_storefronts = []
    for sf in storefronts:
        if is_public is not None and sf.is_public != is_public:
            continue
        if maintenance_mode is not None and sf.maintenance_mode != maintenance_mode:
            continue
        filtered_storefronts.append(sf)
    
    # Contar total (esto es una estimación, en producción sería mejor una consulta COUNT)
    total = len(filtered_storefronts)
    
    # Aplicar paginación manualmente
    start_idx = min(offset, total)
    end_idx = min(offset + page_size, total)
    paginated_storefronts = filtered_storefronts[start_idx:end_idx]
    
    # Calcular páginas
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1
    
    return StorefrontListResponse(
        items=[
            StorefrontResponse(
                **sf.to_dict(),
                api_key_exists=bool(sf.api_key)
            )
            for sf in paginated_storefronts
        ],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get(
    "/{storefront_id}",
    response_model=StorefrontResponse,
    summary="Obtener una tienda",
    description="Obtiene los detalles de una tienda por su ID."
)
async def get_storefront(
    storefront_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin)
) -> StorefrontResponse:
    """
    Obtiene una tienda por su ID.
    
    Args:
        storefront_id: ID de la tienda
        session: Sesión de base de datos
        current_user: Usuario administrador autenticado
        
    Returns:
        StorefrontResponse: Tienda encontrada
    """
    storefront_repo = StorefrontRepository(session)
    storefront = await storefront_repo.get_by_id(storefront_id)
    
    if not storefront:
        from app.core.exceptions import NotFoundException
        raise NotFoundException(
            resource_type="Storefront",
            resource_id=storefront_id
        )
    
    return StorefrontResponse(
        **storefront.to_dict(),
        api_key_exists=bool(storefront.api_key)
    )


@router.put(
    "/{storefront_id}",
    response_model=StorefrontResponse,
    summary="Actualizar una tienda",
    description="Actualiza una tienda existente por su ID."
)
async def update_storefront(
    storefront_id: int,
    storefront_data: StorefrontUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin)
) -> StorefrontResponse:
    """
    Actualiza una tienda.
    
    Args:
        storefront_id: ID de la tienda a actualizar
        storefront_data: Datos a actualizar
        session: Sesión de base de datos
        current_user: Usuario administrador autenticado
        
    Returns:
        StorefrontResponse: Tienda actualizada
    """
    storefront_repo = StorefrontRepository(session)
    
    # Verificar que la tienda existe
    existing = await storefront_repo.get_by_id(storefront_id)
    if not existing:
        from app.core.exceptions import NotFoundException
        raise NotFoundException(
            resource_type="Storefront",
            resource_id=storefront_id
        )
    
    # Si se intenta cambiar el código, verificar que no exista otro con ese código
    if storefront_data.code is not None and storefront_data.code != existing.code:
        duplicate = await storefront_repo.get_by_code(storefront_data.code)
        if duplicate:
            from app.core.exceptions import ConflictException
            raise ConflictException(
                resource_type="Storefront",
                resource_id=storefront_data.code,
                details={"field": "code", "value": storefront_data.code}
            )
    
    # Si se intenta cambiar el dominio, verificar que no exista otro con ese dominio
    if storefront_data.domain is not None and storefront_data.domain != existing.domain:
        duplicate = await storefront_repo.get_by_domain(storefront_data.domain)
        if duplicate:
            from app.core.exceptions import ConflictException
            raise ConflictException(
                resource_type="Storefront",
                resource_id=storefront_data.domain,
                details={"field": "domain", "value": storefront_data.domain}
            )
    
    # Convertir a diccionario, excluyendo campos no establecidos
    update_dict = storefront_data.model_dump(exclude_unset=True)
    
    # Actualizar tienda
    updated = await storefront_repo.update(storefront_id, update_dict)
    if not updated:
        from app.core.exceptions import InternalServerErrorException
        raise InternalServerErrorException(
            message="Error al actualizar la tienda",
            details={"storefront_id": storefront_id}
        )
    
    return StorefrontResponse(
        **updated.to_dict(),
        api_key_exists=bool(updated.api_key)
    )


@router.delete(
    "/{storefront_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una tienda",
    description="Elimina una tienda por su ID. Nota: También elimina usuarios asociados."
)
async def delete_storefront(
    storefront_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin)
) -> None:
    """
    Elimina una tienda.
    
    Args:
        storefront_id: ID de la tienda a eliminar
        session: Sesión de base de datos
        current_user: Usuario administrador autenticado
        
    Raises:
        NotFoundException: Si la tienda no existe
    """
    storefront_repo = StorefrontRepository(session)
    
    # Verificar que la tienda existe
    storefront = await storefront_repo.get_by_id(storefront_id)
    if not storefront:
        from app.core.exceptions import NotFoundException
        raise NotFoundException(
            resource_type="Storefront",
            resource_id=storefront_id
        )
    
    # Eliminar tienda (esto eliminará también usuarios asociados por cascade)
    deleted = await storefront_repo.delete(storefront_id)
    if not deleted:
        from app.core.exceptions import InternalServerErrorException
        raise InternalServerErrorException(
            message="Error al eliminar la tienda",
            details={"storefront_id": storefront_id}
        )
    
    # No content response
    return None


# ---------- Endpoints para API Keys ----------

@router.post(
    "/{storefront_id}/api-keys",
    response_model=StorefrontAPIKeyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generar nueva API Key",
    description="Genera una nueva API Key para una tienda. La clave anterior se invalida."
)
async def generate_new_api_key(
    storefront_id: int,
    key_data: StorefrontAPIKeyGenerate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin)
) -> StorefrontAPIKeyResponse:
    """
    Genera una nueva API Key para una tienda.
    
    Args:
        storefront_id: ID de la tienda
        key_data: Datos para la nueva API Key
        session: Sesión de base de datos
        current_user: Usuario administrador autenticado
        
    Returns:
        StorefrontAPIKeyResponse: Nueva API Key generada
    """
    from datetime import datetime, timedelta
    
    storefront_repo = StorefrontRepository(session)
    
    # Verificar que la tienda existe
    storefront = await storefront_repo.get_by_id(storefront_id)
    if not storefront:
        from app.core.exceptions import NotFoundException
        raise NotFoundException(
            resource_type="Storefront",
            resource_id=storefront_id
        )
    
    # Generar nueva API Key
    new_api_key = generate_storefront_api_key()
    new_api_secret = generate_api_secret()
    
    # Calcular fecha de expiración si se especifica
    expires_at = None
    if key_data.expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=key_data.expires_in_days)
    
    # Crear un ID único para esta API Key
    api_key_id = f"key_{secrets.token_hex(8)}"
    
    # Actualizar tienda con nueva API Key
    update_data = {
        "api_key": new_api_key,
        "api_secret": new_api_secret,
    }
    
    # Si hay webhook URL pero no secret, generar uno nuevo
    if storefront.webhook_url and not storefront.webhook_secret:
        update_data["webhook_secret"] = generate_webhook_secret()
    
    updated = await storefront_repo.update(storefront_id, update_data)
    if not updated:
        from app.core.exceptions import InternalServerErrorException
        raise InternalServerErrorException(
            message="Error al actualizar la API Key",
            details={"storefront_id": storefront_id}
        )
    
    return StorefrontAPIKeyResponse(
        api_key=new_api_key,
        api_key_id=api_key_id,
        key_name=key_data.key_name,
        expires_at=expires_at,
        created_at=datetime.utcnow()
    )


@router.delete(
    "/{storefront_id}/api-keys",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Invalidar API Key",
    description="Invalida la API Key actual de una tienda."
)
async def revoke_api_key(
    storefront_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin)
) -> None:
    """
    Invalida la API Key de una tienda.
    
    Args:
        storefront_id: ID de la tienda
        session: Sesión de base de datos
        current_user: Usuario administrador autenticado
    """
    storefront_repo = StorefrontRepository(session)
    
    # Verificar que la tienda existe
    storefront = await storefront_repo.get_by_id(storefront_id)
    if not storefront:
        from app.core.exceptions import NotFoundException
        raise NotFoundException(
            resource_type="Storefront",
            resource_id=storefront_id
        )
    
    # Invalidar API Key (establecer en None)
    await storefront_repo.update(storefront_id, {
        "api_key": None,
        "api_secret": None,
        "webhook_secret": None  # También invalidar webhook secret por seguridad
    })
    
    return None


# ---------- Endpoints para modo mantenimiento ----------

@router.post(
    "/{storefront_id}/maintenance",
    response_model=StorefrontResponse,
    summary="Activar/desactivar modo mantenimiento",
    description="Activa o desactiva el modo mantenimiento de una tienda."
)
async def toggle_maintenance_mode(
    storefront_id: int,
    enable: bool = Query(..., description="True para activar, False para desactivar"),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin)
) -> StorefrontResponse:
    """
    Activa o desactiva el modo mantenimiento de una tienda.
    
    Args:
        storefront_id: ID de la tienda
        enable: True para activar, False para desactivar
        session: Sesión de base de datos
        current_user: Usuario administrador autenticado
        
    Returns:
        StorefrontResponse: Tienda actualizada
    """
    storefront_repo = StorefrontRepository(session)
    
    # Verificar que la tienda existe
    storefront = await storefront_repo.get_by_id(storefront_id)
    if not storefront:
        from app.core.exceptions import NotFoundException
        raise NotFoundException(
            resource_type="Storefront",
            resource_id=storefront_id
        )
    
    # Actualizar modo mantenimiento
    updated = await storefront_repo.update_maintenance_mode(storefront_id, enable)
    if not updated:
        from app.core.exceptions import InternalServerErrorException
        raise InternalServerErrorException(
            message="Error al actualizar el modo mantenimiento",
            details={"storefront_id": storefront_id}
        )
    
    return StorefrontResponse(
        **updated.to_dict(),
        api_key_exists=bool(updated.api_key)
    )


@router.get(
    "/{storefront_id}/users",
    summary="Obtener usuarios de la tienda",
    description="Obtiene la lista de usuarios asociados a una tienda."
)
async def get_storefront_users(
    storefront_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin)
):
    """
    Obtiene usuarios asociados a una tienda.
    
    Args:
        storefront_id: ID de la tienda
        session: Sesión de base de datos
        current_user: Usuario administrador autenticado
        
    Returns:
        Lista de usuarios de la tienda
    """
    storefront_repo = StorefrontRepository(session)
    
    # Verificar que la tienda existe
    storefront = await storefront_repo.get_by_id(storefront_id)
    if not storefront:
        from app.core.exceptions import NotFoundException
        raise NotFoundException(
            resource_type="Storefront",
            resource_id=storefront_id
        )
    
    # Obtener usuarios (asumiendo que la relación 'users' está cargada)
    # En un caso real, necesitaríamos un método en el repositorio
    from app.repositories.user_repo import UserRepository
    user_repo = UserRepository(session)
    users = await user_repo.get_users_by_storefront(storefront_id)
    
    return {
        "storefront_id": storefront_id,
        "storefront_name": storefront.name,
        "user_count": len(users),
        "users": [
            {
                "id": u.id,
                "email": u.email,
                "first_name": u.first_name,
                "last_name": u.last_name,
                "role": u.role.value if u.role else None,
                "is_active": u.is_active
            }
            for u in users
        ]
    }





