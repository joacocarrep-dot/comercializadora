


"""
Modelos base y mixins para SQLAlchemy.

Este módulo proporciona una base común y mixins reutilizables para todos los modelos.
"""
import uuid
from datetime import datetime
from typing import Any, Dict
from sqlalchemy import Column, DateTime, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, declared_attr
from sqlalchemy.sql import func

# Base común para todos los modelos SQLAlchemy
Base = declarative_base()


class TimestampMixin:
    """
    Mixin que agrega timestamps de creación y actualización.
    
    Atributos:
        created_at (DateTime): Fecha de creación del registro
        updated_at (DateTime): Fecha de última actualización del registro
    """
    
    created_at = Column(DateTime, server_default=func.now(), nullable=False,
                       comment="Fecha de creación del registro")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(),
                       nullable=False, comment="Fecha de última actualización del registro")
    
    def update_timestamp(self) -> None:
        """
        Actualiza manualmente el timestamp de actualización.
        
        Útil cuando se hacen cambios que no disparan automáticamente el onupdate.
        """
        self.updated_at = datetime.utcnow()


class UUIDMixin:
    """
    Mixin que agrega un ID UUID como clave primaria.
    
    Atributos:
        id (UUID): Identificador único universal (UUIDv4)
    """
    
    # Usamos UUID de PostgreSQL para mejor compatibilidad
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
                comment="Identificador único universal (UUIDv4)")
    
    @property
    def uuid_str(self) -> str:
        """
        Obtiene el ID UUID como string.
        
        Returns:
            str: UUID en formato string
        """
        return str(self.id) if self.id else None


class AuditMixin:
    """
    Mixin que agrega campos de auditoría (creado por, actualizado por).
    
    Atributos:
        created_by (UUID): ID del usuario que creó el registro
        updated_by (UUID): ID del usuario que actualizó el registro
    """
    
    created_by = Column(UUID(as_uuid=True), nullable=True,
                        comment="ID del usuario que creó el registro")
    updated_by = Column(UUID(as_uuid=True), nullable=True,
                        comment="ID del usuario que actualizó el registro")


class SoftDeleteMixin:
    """
    Mixin que agrega funcionalidad de soft delete (eliminación lógica).
    
    Atributos:
        is_deleted (bool): Indica si el registro está marcado como eliminado
        deleted_at (DateTime): Fecha de eliminación lógica
        deleted_by (UUID): ID del usuario que eliminó el registro
    """
    
    is_deleted = Column(Boolean, default=False, nullable=False,
                        comment="Indica si el registro está marcado como eliminado")
    deleted_at = Column(DateTime, nullable=True,
                        comment="Fecha de eliminación lógica")
    deleted_by = Column(UUID(as_uuid=True), nullable=True,
                        comment="ID del usuario que eliminó el registro")
    
    def soft_delete(self, user_id: uuid.UUID = None) -> None:
        """
        Marca el registro como eliminado lógicamente.
        
        Args:
            user_id: ID del usuario que realiza la eliminación
        """
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        self.deleted_by = user_id
        self.update_timestamp()
    
    def restore(self) -> None:
        """
        Restaura un registro marcado como eliminado.
        """
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        self.update_timestamp()


class BaseModel(Base, TimestampMixin):
    """
    Modelo base que incluye timestamps y configuración común.
    
    Esta clase combina la Base de SQLAlchemy con el TimestampMixin
    para proporcionar una base común a todos los modelos.
    """
    
    __abstract__ = True
    
    @declared_attr
    def __tablename__(cls) -> str:
        """
        Genera automáticamente el nombre de la tabla en plural y snake_case.
        
        Returns:
            str: Nombre de la tabla
        """
        # Convierte el nombre de la clase a snake_case y lo pluraliza
        name = cls.__name__
        snake_case = ''.join(['_' + c.lower() if c.isupper() else c for c in name]).lstrip('_')
        # Pluralización simple (añade 's' al final)
        if snake_case.endswith('y'):
            return snake_case[:-1] + 'ies'
        elif snake_case.endswith(('s', 'x', 'z', 'ch', 'sh')):
            return snake_case + 'es'
        else:
            return snake_case + 's'
    
    def to_dict(self, exclude: list = None) -> Dict[str, Any]:
        """
        Convierte el modelo a un diccionario.
        
        Args:
            exclude: Lista de atributos a excluir
            
        Returns:
            Dict[str, Any]: Diccionario con los campos del modelo
        """
        if exclude is None:
            exclude = []
        
        result = {}
        for column in self.__table__.columns:
            column_name = column.name
            if column_name in exclude:
                continue
            
            value = getattr(self, column_name)
            
            # Convertir tipos especiales
            if isinstance(value, datetime):
                value = value.isoformat()
            elif isinstance(value, uuid.UUID):
                value = str(value)
            
            result[column_name] = value
        
        return result
    
    def update_from_dict(self, data: Dict[str, Any], exclude: list = None) -> None:
        """
        Actualiza el modelo desde un diccionario.
        
        Args:
            data: Diccionario con datos a actualizar
            exclude: Lista de atributos a excluir de la actualización
        """
        if exclude is None:
            exclude = []
        
        for key, value in data.items():
            if hasattr(self, key) and key not in exclude:
                setattr(self, key, value)
        
        # Actualizar timestamp manualmente
        self.update_timestamp()


class UUIDBaseModel(BaseModel, UUIDMixin):
    """
    Modelo base que usa UUID como clave primaria e incluye timestamps.
    
    Esta clase combina BaseModel con UUIDMixin para modelos que requieren
    identificadores únicos universales.
    """
    __abstract__ = True


# Alias comunes para conveniencia
Model = Base
UUIDModel = UUIDBaseModel


# Función de utilidad para obtener todos los modelos
def get_all_models() -> list:
    """
    Obtiene una lista de todos los modelos que heredan de Base.
    
    Returns:
        list: Lista de clases de modelo
    """
    return Base.__subclasses__()


