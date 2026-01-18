

"""
Repositorio específico para el modelo Storefront.

Proporciona métodos personalizados para operaciones relacionadas con tiendas virtuales,
además de heredar todas las operaciones CRUD genéricas de BaseRepository.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, and_

from app.models.storefront import Storefront
from app.repositories.base import BaseRepository


class StorefrontRepository(BaseRepository[Storefront]):
    """
    Repositorio para operaciones con tiendas virtuales (Storefront).
    
    Hereda de BaseRepository y añade métodos específicos para tiendas.
    """
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Storefront)
    
    async def get_by_code(self, code: str) -> Optional[Storefront]:
        """
        Obtiene una tienda por su código único.
        
        Args:
            code: Código único de la tienda
            
        Returns:
            La tienda encontrada o None si no existe
        """
        query = select(self.model).where(self.model.code == code)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_domain(self, domain: str) -> Optional[Storefront]:
        """
        Obtiene una tienda por su dominio.
        
        Args:
            domain: Dominio de la tienda
            
        Returns:
            La tienda encontrada o None si no existe
        """
        query = select(self.model).where(self.model.domain == domain)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def search(
        self,
        search_term: str,
        skip: int = 0,
        limit: int = 100,
        only_active: bool = True
    ) -> List[Storefront]:
        """
        Busca tiendas por término de búsqueda (en nombre, código, dominio o email).
        
        Args:
            search_term: Término de búsqueda
            skip: Número de registros a omitir
            limit: Número máximo de registros a devolver
            only_active: Si True, solo devuelve tiendas activas
            
        Returns:
            Lista de tiendas que coinciden con la búsqueda
        """
        query = select(self.model)
        
        # Construir condiciones de búsqueda
        search_conditions = []
        if search_term:
            search_term_like = f"%{search_term}%"
            search_conditions.extend([
                self.model.name.ilike(search_term_like),
                self.model.code.ilike(search_term_like),
                self.model.domain.ilike(search_term_like),
                self.model.contact_email.ilike(search_term_like),
                self.model.support_email.ilike(search_term_like)
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
    
    async def get_public_storefronts(self) -> List[Storefront]:
        """
        Obtiene todas las tiendas públicas y activas.
        
        Returns:
            Lista de tiendas públicas activas
        """
        query = select(self.model).where(
            and_(
                self.model.is_active == True,
                self.model.is_public == True
            )
        ).order_by(self.model.name)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_active_storefronts(self) -> List[Storefront]:
        """
        Obtiene todas las tiendas activas.
        
        Returns:
            Lista de tiendas activas
        """
        query = select(self.model).where(
            self.model.is_active == True
        ).order_by(self.model.name)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_storefronts_by_category(self, category: str) -> List[Storefront]:
        """
        Obtiene tiendas que tienen una categoría específica.
        
        Args:
            category: Categoría a buscar
            
        Returns:
            Lista de tiendas que incluyen la categoría
        """
        # Buscar en el array de categorías
        query = select(self.model).where(
            and_(
                self.model.is_active == True,
                self.model.categories.any(category)
            )
        ).order_by(self.model.name)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def count_by_status(self) -> Dict[str, int]:
        """
        Cuenta tiendas por estado (activas/inactivas) y visibilidad (públicas/privadas).
        
        Returns:
            Diccionario con conteos por estado
        """
        # Contar activas
        active_public = await self.session.execute(
            select(self.model.id).where(
                and_(
                    self.model.is_active == True,
                    self.model.is_public == True
                )
            )
        )
        active_public_count = len(active_public.scalars().all())
        
        active_private = await self.session.execute(
            select(self.model.id).where(
                and_(
                    self.model.is_active == True,
                    self.model.is_public == False
                )
            )
        )
        active_private_count = len(active_private.scalars().all())
        
        # Contar inactivas
        inactive = await self.session.execute(
            select(self.model.id).where(self.model.is_active == False)
        )
        inactive_count = len(inactive.scalars().all())
        
        return {
            "active_public": active_public_count,
            "active_private": active_private_count,
            "inactive": inactive_count,
            "total": active_public_count + active_private_count + inactive_count
        }
    
    async def update_maintenance_mode(self, storefront_id: int, maintenance_mode: bool) -> Optional[Storefront]:
        """
        Activa o desactiva el modo mantenimiento de una tienda.
        
        Args:
            storefront_id: ID de la tienda
            maintenance_mode: True para activar modo mantenimiento, False para desactivar
            
        Returns:
            La tienda actualizada o None si no existe
        """
        return await self.update(storefront_id, {"maintenance_mode": maintenance_mode})
    
    async def get_storefronts_with_payment_config(self) -> List[Storefront]:
        """
        Obtiene tiendas que tienen configuración de pagos.
        
        Returns:
            Lista de tiendas con configuración de pagos
        """
        query = select(self.model).where(
            and_(
                self.model.is_active == True,
                self.model.payment_config.isnot(None)
            )
        ).order_by(self.model.name)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_storefronts_by_tag(self, tag: str) -> List[Storefront]:
        """
        Obtiene tiendas que tienen una etiqueta específica.
        
        Args:
            tag: Etiqueta a buscar
            
        Returns:
            Lista de tiendas que incluyen la etiqueta
        """
        query = select(self.model).where(
            and_(
                self.model.is_active == True,
                self.model.tags.any(tag)
            )
        ).order_by(self.model.name)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())



