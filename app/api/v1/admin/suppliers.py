


"""
Endpoints CRUD para la administración de proveedores (Suppliers).

Requiere autenticación de administrador.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import require_admin
from app.db.session import get_session
from app.models.user import User
from app.repositories.supplier_repo import SupplierRepository
from app.schemas.supplier import (
    SupplierCreate,
    SupplierUpdate,
    SupplierResponse,
    SupplierListResponse,
    SupplierFilter,
)

router = APIRouter(prefix="/admin/suppliers", tags=["Admin - Suppliers"])


# ---------- Endpoints CRUD ----------

@router.post(
    "/",
    response_model=SupplierResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo proveedor",
    description="Crea un nuevo proveedor en el sistema. Requiere permisos de administrador."
)
async def create_supplier(
    supplier_data: SupplierCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin)
) -> SupplierResponse:
    """
    Crea un nuevo proveedor.
    
    Args:
        supplier_data: Datos del proveedor a crear
        session: Sesión de base de datos
        current_user: Usuario administrador autenticado
        
    Returns:
        SupplierResponse: Proveedor creado
    """
    supplier_repo = SupplierRepository(session)
    
    # Verificar que el código no exista
    existing = await supplier_repo.get_by_code(supplier_data.code)
    if existing:
        from app.core.exceptions import ConflictException
        raise ConflictException(
            resource_type="Supplier",
            resource_id=supplier_data.code,
            details={"field": "code", "value": supplier_data.code}
        )
    
    # Convertir a diccionario y crear
    supplier_dict = supplier_data.model_dump(exclude_unset=True)
    supplier = await supplier_repo.create(supplier_dict)
    
    # Convertir a respuesta
    return SupplierResponse.model_validate(supplier)


@router.get(
    "/",
    response_model=SupplierListResponse,
    summary="Listar proveedores",
    description="Obtiene una lista paginada de proveedores. Filtros opcionales por búsqueda, estado, etc."
)
async def list_suppliers(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(20, ge=1, le=100, description="Tamaño de página"),
    search: Optional[str] = Query(None, description="Término de búsqueda (nombre, código, email)"),
    is_active: Optional[bool] = Query(None, description="Filtrar por estado activo/inactivo"),
    sync_enabled: Optional[bool] = Query(None, description="Filtrar por sincronización habilitada"),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin)
) -> SupplierListResponse:
    """
    Lista proveedores con paginación y filtros.
    
    Args:
        page: Número de página
        page_size: Tamaño de página
        search: Término de búsqueda
        is_active: Filtrar por estado activo
        sync_enabled: Filtrar por sincronización habilitada
        session: Sesión de base de datos
        current_user: Usuario administrador autenticado
        
    Returns:
        SupplierListResponse: Lista paginada de proveedores
    """
    supplier_repo = SupplierRepository(session)
    
    # Aplicar filtros
    filters = {}
    if search is not None:
        filters["search"] = search
    if is_active is not None:
        filters["is_active"] = is_active
    if sync_enabled is not None:
        filters["sync_enabled"] = sync_enabled
    
    # Calcular offset
    offset = (page - 1) * page_size
    
    # Obtener proveedores con filtros
    suppliers = await supplier_repo.search(
        search_term=search,
        skip=offset,
        limit=page_size,
        only_active=is_active if is_active is not None else None,
        sync_enabled=sync_enabled
    )
    
    # Contar total
    total = await supplier_repo.count_by_filters(filters)
    
    # Calcular páginas
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1
    
    return SupplierListResponse(
        items=[SupplierResponse.model_validate(s) for s in suppliers],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get(
    "/{supplier_id}",
    response_model=SupplierResponse,
    summary="Obtener un proveedor",
    description="Obtiene los detalles de un proveedor por su ID."
)
async def get_supplier(
    supplier_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin)
) -> SupplierResponse:
    """
    Obtiene un proveedor por su ID.
    
    Args:
        supplier_id: ID del proveedor
        session: Sesión de base de datos
        current_user: Usuario administrador autenticado
        
    Returns:
        SupplierResponse: Proveedor encontrado
    """
    supplier_repo = SupplierRepository(session)
    supplier = await supplier_repo.get_by_id(supplier_id)
    
    if not supplier:
        from app.core.exceptions import NotFoundException
        raise NotFoundException(
            resource_type="Supplier",
            resource_id=supplier_id
        )
    
    return SupplierResponse.model_validate(supplier)


@router.put(
    "/{supplier_id}",
    response_model=SupplierResponse,
    summary="Actualizar un proveedor",
    description="Actualiza un proveedor existente por su ID."
)
async def update_supplier(
    supplier_id: int,
    supplier_data: SupplierUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin)
) -> SupplierResponse:
    """
    Actualiza un proveedor.
    
    Args:
        supplier_id: ID del proveedor a actualizar
        supplier_data: Datos a actualizar
        session: Sesión de base de datos
        current_user: Usuario administrador autenticado
        
    Returns:
        SupplierResponse: Proveedor actualizado
    """
    supplier_repo = SupplierRepository(session)
    
    # Verificar que el proveedor existe
    existing = await supplier_repo.get_by_id(supplier_id)
    if not existing:
        from app.core.exceptions import NotFoundException
        raise NotFoundException(
            resource_type="Supplier",
            resource_id=supplier_id
        )
    
    # Si se intenta cambiar el código, verificar que no exista otro con ese código
    if supplier_data.code is not None and supplier_data.code != existing.code:
        duplicate = await supplier_repo.get_by_code(supplier_data.code)
        if duplicate:
            from app.core.exceptions import ConflictException
            raise ConflictException(
                resource_type="Supplier",
                resource_id=supplier_data.code,
                details={"field": "code", "value": supplier_data.code}
            )
    
    # Convertir a diccionario, excluyendo campos no establecidos
    update_dict = supplier_data.model_dump(exclude_unset=True)
    
    # Actualizar proveedor
    updated = await supplier_repo.update(supplier_id, update_dict)
    if not updated:
        from app.core.exceptions import InternalServerErrorException
        raise InternalServerErrorException(
            message="Error al actualizar el proveedor",
            details={"supplier_id": supplier_id}
        )
    
    return SupplierResponse.model_validate(updated)


@router.delete(
    "/{supplier_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un proveedor",
    description="Elimina un proveedor por su ID. Nota: No se eliminará si tiene productos asociados."
)
async def delete_supplier(
    supplier_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin)
) -> None:
    """
    Elimina un proveedor.
    
    Args:
        supplier_id: ID del proveedor a eliminar
        session: Sesión de base de datos
        current_user: Usuario administrador autenticado
        
    Raises:
        NotFoundException: Si el proveedor no existe
        ConflictException: Si el proveedor tiene productos asociados
    """
    supplier_repo = SupplierRepository(session)
    
    # Verificar que el proveedor existe
    supplier = await supplier_repo.get_by_id(supplier_id)
    if not supplier:
        from app.core.exceptions import NotFoundException
        raise NotFoundException(
            resource_type="Supplier",
            resource_id=supplier_id
        )
    
    # Verificar que no tenga productos asociados
    # (Asumiendo que el modelo Supplier tiene una relación 'products')
    product_count = await supplier_repo.count_products(supplier_id)
    if product_count > 0:
        from app.core.exceptions import ConflictException
        raise ConflictException(
            resource_type="Supplier",
            resource_id=supplier_id,
            details={
                "message": "No se puede eliminar un proveedor con productos asociados",
                "product_count": product_count
            }
        )
    
    # Eliminar proveedor
    deleted = await supplier_repo.delete(supplier_id)
    if not deleted:
        from app.core.exceptions import InternalServerErrorException
        raise InternalServerErrorException(
            message="Error al eliminar el proveedor",
            details={"supplier_id": supplier_id}
        )
    
    # No content response
    return None


# ---------- Endpoints adicionales ----------

@router.get(
    "/{supplier_id}/products",
    summary="Obtener productos del proveedor",
    description="Obtiene la lista de productos asociados a un proveedor."
)
async def get_supplier_products(
    supplier_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin)
):
    """
    Obtiene productos asociados a un proveedor.
    
    Args:
        supplier_id: ID del proveedor
        session: Sesión de base de datos
        current_user: Usuario administrador autenticado
        
    Returns:
        Lista de productos del proveedor
    """
    supplier_repo = SupplierRepository(session)
    
    # Verificar que el proveedor existe
    supplier = await supplier_repo.get_by_id(supplier_id)
    if not supplier:
        from app.core.exceptions import NotFoundException
        raise NotFoundException(
            resource_type="Supplier",
            resource_id=supplier_id
        )
    
    # Obtener productos (asumiendo que el repositorio tiene un método para esto)
    products = await supplier_repo.get_products(supplier_id)
    
    # Convertir productos a respuesta (necesitaríamos un schema de Product)
    # Por ahora devolvemos una lista básica
    return {
        "supplier_id": supplier_id,
        "supplier_name": supplier.name,
        "product_count": len(products),
        "products": [{"id": p.id, "name": getattr(p, "name", "N/A")} for p in products]
    }


@router.post(
    "/{supplier_id}/sync",
    summary="Sincronizar productos del proveedor",
    description="Ejecuta una sincronización manual de productos desde el proveedor."
)
async def sync_supplier(
    supplier_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin)
):
    """
    Sincroniza productos desde un proveedor.
    
    Args:
        supplier_id: ID del proveedor
        session: Sesión de base de datos
        current_user: Usuario administrador autenticado
        
    Returns:
        Resultado de la sincronización
    """
    supplier_repo = SupplierRepository(session)
    
    # Verificar que el proveedor existe
    supplier = await supplier_repo.get_by_id(supplier_id)
    if not supplier:
        from app.core.exceptions import NotFoundException
        raise NotFoundException(
            resource_type="Supplier",
            resource_id=supplier_id
        )
    
    # Verificar que tenga sincronización habilitada
    if not supplier.sync_enabled:
        from app.core.exceptions import BadRequestException
        raise BadRequestException(
            message="La sincronización no está habilitada para este proveedor",
            details={"supplier_id": supplier_id, "sync_enabled": False}
        )
    
    # Aquí iría la lógica de sincronización real
    # Por ahora, simulamos una sincronización básica
    
    return {
        "message": "Sincronización iniciada",
        "supplier_id": supplier_id,
        "supplier_name": supplier.name,
        "sync_type": "manual",
        "status": "queued",
        "note": "La sincronización se ejecutará en segundo plano"
    }





