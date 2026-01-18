

"""
Repositorio específico para el modelo Supplier.

Proporciona métodos personalizados para operaciones relacionadas con proveedores,
además de heredar todas las operaciones CRUD genéricas de BaseRepository.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, and_

from app.models.supplier import Supplier
from app.repositories.base import BaseRepository


class SupplierRepository(BaseRepository[Supplier]):
    """
    Repositorio para operaciones con proveedores (Supplier).
    
    Hereda de BaseRepository y añade métodos específicos para proveedores.
    """
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Supplier)
    
    async def get_by_code(self, code: str) -> Optional[Supplier]:
        """
        Obtiene un proveedor por su código único.
        
        Args:
            code: Código único del proveedor
            
        Returns:
            El proveedor encontrado o None si no existe
        """
        query = select(self.model).where(self.model.code == code)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def search(
        self,
        search_term: str,
        skip: int = 0,
        limit: int = 100,
        only_active: bool = True
    ) -> List[Supplier]:
        """
        Busca proveedores por término de búsqueda (en nombre, código o email).
        
        Args:
            search_term: Término de búsqueda
            skip: Número de registros a omitir
            limit: Número máximo de registros a devolver
            only_active: Si True, solo devuelve proveedores activos
            
        Returns:
            Lista de proveedores que coinciden con la búsqueda
        """
        query = select(self.model)
        
        # Construir condiciones de búsqueda
        search_conditions = []
        if search_term:
            search_term_like = f"%{search_term}%"
            search_conditions.extend([
                self.model.name.ilike(search_term_like),
                self.model.code.ilike(search_term_like),
                self.model.contact_name.ilike(search_term_like),
                self.model.contact_email.ilike(search_term_like)
            ])
        
        # Aplicar condiciones
        if search_conditions:
            query = query.where(or_(*search_conditions))
        
        if only_active:
            query = query.where(self.model.is_active == True)
        
        # Aplicar paginación
        query = query.offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_active_suppliers(self) -> List[Supplier]:
        """
        Obtiene todos los proveedores activos.
        
        Returns:
            Lista de proveedores activos
        """
        query = select(self.model).where(
            and_(
                self.model.is_active == True,
                self.model.sync_enabled == True
            )
        ).order_by(self.model.name)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def update_sync_status(
        self, 
        supplier_id: int, 
        last_sync_at: str, 
        success: bool = True
    ) -> Optional[Supplier]:
        """
        Actualiza el estado de sincronización de un proveedor.
        
        Args:
            supplier_id: ID del proveedor
            last_sync_at: Fecha/hora de la última sincronización (ISO string)
            success: Si la sincronización fue exitosa
            
        Returns:
            El proveedor actualizado o None si no existe
        """
        data = {"last_sync_at": last_sync_at}
        
        # Si la sincronización falló, podríamos querer registrar algún error
        # Por ahora solo actualizamos la fecha
        return await self.update(supplier_id, data)
    
    async def get_suppliers_with_api_config(self) -> List[Supplier]:
        """
        Obtiene proveedores que tienen configuración de API completa.
        
        Returns:
            Lista de proveedores con API configurada
        """
        query = select(self.model).where(
            and_(
                self.model.is_active == True,
                self.model.api_endpoint.isnot(None),
                self.model.api_key.isnot(None)
            )
        ).order_by(self.model.name)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def count_by_status(self) -> Dict[str, int]:
        """
        Cuenta proveedores por estado (activos/inactivos).
        
        Returns:
            Diccionario con conteos por estado
        """
        # Contar activos
        active_query = select(self.model).where(self.model.is_active == True)
        active_result = await self.session.execute(select(self.model.id).where(self.model.is_active == True))
        active_count = len(active_result.scalars().all())
        
        # Contar inactivos
        inactive_query = select(self.model).where(self.model.is_active == False)
        inactive_result = await self.session.execute(select(self.model.id).where(self.model.is_active == False))
        inactive_count = len(inactive_result.scalars().all())
        
        return {
            "active": active_count,
            "inactive": inactive_count,
            "total": active_count + inactive_count
        }


