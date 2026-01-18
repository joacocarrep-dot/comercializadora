
"""
Repositorio base con operaciones CRUD genéricas asíncronas.

Proporciona métodos comunes para interactuar con cualquier modelo SQLAlchemy,
implementando el patrón Repository para separar la lógica de acceso a datos.
"""

from typing import Type, TypeVar, Generic, List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update as sql_update, delete as sql_delete
from sqlalchemy.sql import func
from sqlalchemy.orm import selectinload

from app.models.base import Base

# Tipo genérico para el modelo
ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Repositorio base que proporciona operaciones CRUD asíncronas para cualquier modelo.
    
    Args:
        session: Sesión asíncrona de SQLAlchemy
        model: Clase del modelo SQLAlchemy
    """
    
    def __init__(self, session: AsyncSession, model: Type[ModelType]):
        self.session = session
        self.model = model
    
    async def get_by_id(self, id: int, include_related: Optional[List[str]] = None) -> Optional[ModelType]:
        """
        Obtiene un registro por su ID.
        
        Args:
            id: ID del registro
            include_related: Lista opcional de relaciones a cargar (eager loading)
            
        Returns:
            El registro encontrado o None si no existe
        """
        query = select(self.model).where(self.model.id == id)
        
        if include_related:
            for relation in include_related:
                query = query.options(selectinload(getattr(self.model, relation)))
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        include_related: Optional[List[str]] = None
    ) -> List[ModelType]:
        """
        Obtiene todos los registros con paginación y filtros opcionales.
        
        Args:
            skip: Número de registros a omitir (para paginación)
            limit: Número máximo de registros a devolver
            filters: Diccionario de filtros {campo: valor}
            order_by: Campo por el que ordenar (opcional)
            include_related: Lista opcional de relaciones a cargar
            
        Returns:
            Lista de registros
        """
        query = select(self.model)
        
        # Aplicar filtros
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    if isinstance(value, list):
                        # Para filtros IN
                        query = query.where(getattr(self.model, field).in_(value))
                    else:
                        query = query.where(getattr(self.model, field) == value)
        
        # Aplicar ordenamiento
        if order_by:
            if order_by.startswith("-"):
                # Orden descendente
                field = order_by[1:]
                if hasattr(self.model, field):
                    query = query.order_by(getattr(self.model, field).desc())
            else:
                # Orden ascendente
                if hasattr(self.model, order_by):
                    query = query.order_by(getattr(self.model, order_by))
        
        # Aplicar paginación
        query = query.offset(skip).limit(limit)
        
        # Cargar relaciones
        if include_related:
            for relation in include_related:
                query = query.options(selectinload(getattr(self.model, relation)))
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def create(self, data: Dict[str, Any]) -> ModelType:
        """
        Crea un nuevo registro.
        
        Args:
            data: Diccionario con los datos del registro
            
        Returns:
            El registro creado
        """
        # Filtrar solo los campos que existen en el modelo
        model_fields = {k: v for k, v in data.items() if hasattr(self.model, k)}
        instance = self.model(**model_fields)
        
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        
        return instance
    
    async def update(self, id: int, data: Dict[str, Any]) -> Optional[ModelType]:
        """
        Actualiza un registro existente.
        
        Args:
            id: ID del registro a actualizar
            data: Diccionario con los datos a actualizar
            
        Returns:
            El registro actualizado o None si no existe
        """
        # Filtrar solo los campos que existen en el modelo
        model_fields = {k: v for k, v in data.items() if hasattr(self.model, k)}
        
        if not model_fields:
            return None
        
        # Ejecutar update
        stmt = (
            sql_update(self.model)
            .where(self.model.id == id)
            .values(**model_fields)
            .execution_options(synchronize_session="fetch")
        )
        
        await self.session.execute(stmt)
        
        # Devolver el registro actualizado
        return await self.get_by_id(id)
    
    async def delete(self, id: int) -> bool:
        """
        Elimina un registro por su ID.
        
        Args:
            id: ID del registro a eliminar
            
        Returns:
            True si se eliminó, False si no existe
        """
        instance = await self.get_by_id(id)
        if not instance:
            return False
        
        await self.session.delete(instance)
        await self.session.flush()
        return True
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Cuenta el número total de registros que coinciden con los filtros.
        
        Args:
            filters: Diccionario de filtros {campo: valor}
            
        Returns:
            Número total de registros
        """
        query = select(func.count()).select_from(self.model)
        
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    if isinstance(value, list):
                        query = query.where(getattr(self.model, field).in_(value))
                    else:
                        query = query.where(getattr(self.model, field) == value)
        
        result = await self.session.execute(query)
        return result.scalar_one()
    
    async def exists(self, id: int) -> bool:
        """
        Verifica si un registro existe por su ID.
        
        Args:
            id: ID del registro
            
        Returns:
            True si existe, False si no
        """
        query = select(func.count()).where(self.model.id == id)
        result = await self.session.execute(query)
        count = result.scalar_one()
        return count > 0

