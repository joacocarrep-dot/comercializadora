



"""
Repositorio específico para el modelo User.

Proporciona métodos personalizados para operaciones relacionadas con usuarios,
además de heredar todas las operaciones CRUD genéricas de BaseRepository.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, and_

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """
    Repositorio para operaciones con usuarios (User).
    
    Hereda de BaseRepository y añade métodos específicos para usuarios.
    """
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, User)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Obtiene un usuario por su email.
        
        Args:
            email: Email del usuario
            
        Returns:
            El usuario encontrado o None si no existe
        """
        query = select(self.model).where(self.model.email == email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """
        Obtiene un usuario por su nombre de usuario.
        
        Nota: El modelo User actual no tiene campo 'username', 
        pero se incluye para futura compatibilidad.
        
        Args:
            username: Nombre de usuario
            
        Returns:
            El usuario encontrado o None si no existe
        """
        # Por ahora, el email actúa como username
        return await self.get_by_email(username)
    
    async def search(
        self,
        search_term: str,
        skip: int = 0,
        limit: int = 100,
        only_active: bool = True
    ) -> List[User]:
        """
        Busca usuarios por término de búsqueda (en email, nombre, apellido).
        
        Args:
            search_term: Término de búsqueda
            skip: Número de registros a omitir
            limit: Número máximo de registros a devolver
            only_active: Si True, solo devuelve usuarios activos
            
        Returns:
            Lista de usuarios que coinciden con la búsqueda
        """
        query = select(self.model)
        
        # Construir condiciones de búsqueda
        search_conditions = []
        if search_term:
            search_term_like = f"%{search_term}%"
            search_conditions.extend([
                self.model.email.ilike(search_term_like),
                self.model.first_name.ilike(search_term_like),
                self.model.last_name.ilike(search_term_like),
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
    
    async def get_users_by_role(self, role: str) -> List[User]:
        """
        Obtiene usuarios por rol.
        
        Args:
            role: Rol a buscar (superadmin, admin, operator)
            
        Returns:
            Lista de usuarios con el rol especificado
        """
        query = select(self.model).where(
            and_(
                self.model.is_active == True,
                self.model.role == role
            )
        ).order_by(self.model.email)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_users_by_storefront(self, storefront_id: int) -> List[User]:
        """
        Obtiene usuarios asociados a un storefront específico.
        
        Args:
            storefront_id: ID del storefront
            
        Returns:
            Lista de usuarios del storefront
        """
        query = select(self.model).where(
            and_(
                self.model.is_active == True,
                self.model.storefront_id == storefront_id
            )
        ).order_by(self.model.email)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_admins(self) -> List[User]:
        """
        Obtiene todos los usuarios administradores (admin y superadmin).
        
        Returns:
            Lista de usuarios administradores
        """
        query = select(self.model).where(
            and_(
                self.model.is_active == True,
                or_(
                    self.model.role == "admin",
                    self.model.role == "superadmin"
                )
            )
        ).order_by(self.model.email)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def count_by_role(self) -> Dict[str, int]:
        """
        Cuenta usuarios por rol.
        
        Returns:
            Diccionario con conteos por rol
        """
        # Contar por cada rol
        roles = ["superadmin", "admin", "operator"]
        counts = {}
        
        for role in roles:
            query = select(self.model.id).where(
                and_(
                    self.model.is_active == True,
                    self.model.role == role
                )
            )
            result = await self.session.execute(query)
            counts[role] = len(result.scalars().all())
        
        # Contar total
        total_query = select(self.model.id).where(self.model.is_active == True)
        total_result = await self.session.execute(total_query)
        counts["total"] = len(total_result.scalars().all())
        
        return counts
    
    async def get_with_storefront(self, user_id: int) -> Optional[User]:
        """
        Obtiene un usuario incluyendo la relación con su storefront.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            El usuario con la relación storefront cargada
        """
        query = select(self.model).where(
            self.model.id == user_id
        ).options(selectinload(self.model.storefront))
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def update_last_login(self, user_id: int) -> Optional[User]:
        """
        Actualiza la fecha de último login del usuario.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            El usuario actualizado o None si no existe
        """
        from datetime import datetime
        return await self.update(user_id, {"last_login_at": datetime.utcnow()})
    
    async def lock_user(self, user_id: int, minutes: int = 15) -> Optional[User]:
        """
        Bloquea un usuario por un tiempo específico.
        
        Args:
            user_id: ID del usuario
            minutes: Minutos de bloqueo
            
        Returns:
            El usuario actualizado o None si no existe
        """
        from datetime import datetime, timedelta
        locked_until = datetime.utcnow() + timedelta(minutes=minutes)
        return await self.update(user_id, {
            "locked_until": locked_until,
            "failed_login_attempts": 5  # Máximo de intentos
        })
    
    async def unlock_user(self, user_id: int) -> Optional[User]:
        """
        Desbloquea un usuario.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            El usuario actualizado o None si no existe
        """
        return await self.update(user_id, {
            "locked_until": None,
            "failed_login_attempts": 0
        })
    
    async def verify_email(self, user_id: int) -> Optional[User]:
        """
        Marca el email de un usuario como verificado.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            El usuario actualizado o None si no existe
        """
        from datetime import datetime
        return await self.update(user_id, {
            "is_verified": True,
            "email_verified_at": datetime.utcnow()
        })




