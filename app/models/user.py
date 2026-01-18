

"""
Modelo SQLAlchemy para Usuarios (Users/Administradores).
"""
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from passlib.context import CryptContext

# Importar base y mixins comunes
from app.models.base import BaseModel

# Configuración para hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserRole(PyEnum):
    """
    Enum para roles de usuario.
    """
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    OPERATOR = "operator"


class User(BaseModel):
    """
    Modelo de Usuario (User/Administrador).
    
    Representa un usuario del sistema con diferentes niveles de acceso.
    
    Hereda de BaseModel que ya incluye:
    - created_at, updated_at (TimestampMixin)
    - Métodos to_dict, update_from_dict, update_timestamp
    """
    __tablename__ = "users"
    
    # Identificación
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), nullable=False, index=True, comment="Email del usuario")
    hashed_password = Column(String(255), nullable=False, comment="Contraseña hasheada")
    
    # Información personal
    first_name = Column(String(100), nullable=True, comment="Nombre del usuario")
    last_name = Column(String(100), nullable=True, comment="Apellido del usuario")
    
    # Roles y permisos
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.OPERATOR,
                  comment="Rol del usuario en el sistema")
    
    # Relación con Storefront
    storefront_id = Column(Integer, ForeignKey("storefronts.id", ondelete="CASCADE"), 
                           nullable=True, comment="ID del storefront al que pertenece")
    
    # Estado
    is_active = Column(Boolean, default=True, nullable=False,
                       comment="Indica si el usuario está activo")
    is_verified = Column(Boolean, default=False, nullable=False,
                         comment="Indica si el usuario ha verificado su email")
    email_verified_at = Column(DateTime, nullable=True,
                               comment="Fecha de verificación del email")
    
    # Seguridad
    last_login_at = Column(DateTime, nullable=True,
                           comment="Última fecha de login")
    failed_login_attempts = Column(Integer, default=0, nullable=False,
                                   comment="Número de intentos fallidos de login")
    locked_until = Column(DateTime, nullable=True,
                          comment="Usuario bloqueado hasta esta fecha")
    
    # Metadatos adicionales (no usar 'metadata' que es reservado por SQLAlchemy)
    extra_metadata = Column(String, nullable=True,
                      comment="Metadatos adicionales en formato JSON")
    
    # Nota: created_at y updated_at ya están definidos en BaseModel (TimestampMixin)
    
    # Relaciones
    # Relación muchos-a-uno con Storefront
    storefront = relationship("Storefront", back_populates="users")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role.value}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte el modelo a un diccionario.
        
        Returns:
            Dict[str, Any]: Diccionario con los campos del usuario
        """
        # Usar el método to_dict de la clase base y luego extenderlo
        base_dict = super().to_dict(exclude=['hashed_password'])
        # Agregar campos específicos o modificar
        base_dict.update({
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "role": self.role.value if self.role else None,
            "storefront_id": self.storefront_id,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "email_verified_at": self.email_verified_at.isoformat() if self.email_verified_at else None,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
            # Nota: created_at y updated_at ya están incluidos por el método base
        })
        return base_dict
    
    # Métodos para manejo de contraseñas
    def verify_password(self, plain_password: str) -> bool:
        """
        Verifica si la contraseña en texto plano coincide con el hash almacenado.
        
        Args:
            plain_password: Contraseña en texto plano
            
        Returns:
            bool: True si la contraseña es correcta, False en caso contrario
        """
        return pwd_context.verify(plain_password, self.hashed_password)
    
    def set_password(self, plain_password: str) -> None:
        """
        Establece una nueva contraseña hasheada.
        
        Args:
            plain_password: Nueva contraseña en texto plano
        """
        self.hashed_password = pwd_context.hash(plain_password)
        self.update_timestamp()
    
    @staticmethod
    def hash_password(plain_password: str) -> str:
        """
        Genera un hash para una contraseña en texto plano.
        
        Args:
            plain_password: Contraseña en texto plano
            
        Returns:
            str: Contraseña hasheada
        """
        return pwd_context.hash(plain_password)
    
    # Métodos para verificación de roles
    def is_superadmin(self) -> bool:
        """
        Verifica si el usuario tiene rol de superadmin.
        
        Returns:
            bool: True si es superadmin, False en caso contrario
        """
        return self.role == UserRole.SUPERADMIN
    
    def is_admin(self) -> bool:
        """
        Verifica si el usuario tiene rol de admin o superior.
        
        Returns:
            bool: True si es admin o superadmin, False en caso contrario
        """
        return self.role in [UserRole.ADMIN, UserRole.SUPERADMIN]
    
    def is_operator(self) -> bool:
        """
        Verifica si el usuario tiene rol de operator o superior.
        
        Returns:
            bool: True si es operator, admin o superadmin, False en caso contrario
        """
        return self.role in [UserRole.OPERATOR, UserRole.ADMIN, UserRole.SUPERADMIN]
    
    def has_role(self, role: UserRole) -> bool:
        """
        Verifica si el usuario tiene un rol específico.
        
        Args:
            role: Rol a verificar
            
        Returns:
            bool: True si tiene el rol, False en caso contrario
        """
        return self.role == role
    
    def has_any_role(self, roles: list) -> bool:
        """
        Verifica si el usuario tiene alguno de los roles especificados.
        
        Args:
            roles: Lista de roles a verificar
            
        Returns:
            bool: True si tiene alguno de los roles, False en caso contrario
        """
        return self.role in roles
    
    # Métodos para manejo de seguridad
    def record_login(self, successful: bool = True) -> None:
        """
        Registra un intento de login.
        
        Args:
            successful: True si el login fue exitoso, False en caso contrario
        """
        if successful:
            self.last_login_at = datetime.utcnow()
            self.failed_login_attempts = 0
            self.locked_until = None
        else:
            self.failed_login_attempts += 1
            # Bloquear usuario después de 5 intentos fallidos por 15 minutos
            if self.failed_login_attempts >= 5:
                self.locked_until = datetime.utcnow().timestamp() + 900  # 15 minutos
        self.update_timestamp()
    
    def is_locked(self) -> bool:
        """
        Verifica si el usuario está bloqueado.
        
        Returns:
            bool: True si el usuario está bloqueado, False en caso contrario
        """
        if not self.locked_until:
            return False
        return datetime.utcnow().timestamp() < self.locked_until


