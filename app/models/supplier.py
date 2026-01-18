
"""
Modelo SQLAlchemy para Proveedores (Suppliers).
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import Column, Integer, String, Text, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

# Importar base y mixins comunes
from app.models.base import BaseModel


class Supplier(BaseModel):
    """
    Modelo de Proveedor (Supplier).
    
    Representa a un proveedor externo de productos que integra con la plataforma
    a través de APIs.
    
    Hereda de BaseModel que ya incluye:
    - created_at, updated_at (TimestampMixin)
    - Métodos to_dict, update_from_dict, update_timestamp
    """
    __tablename__ = "suppliers"
    
    # Identificación
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String(50), unique=True, index=True, nullable=False, 
                  comment="Código único del proveedor")
    name = Column(String(255), nullable=False, comment="Nombre del proveedor")
    
    # Información de contacto
    contact_name = Column(String(255), nullable=True, comment="Nombre de contacto")
    contact_email = Column(String(255), nullable=True, comment="Email de contacto")
    contact_phone = Column(String(50), nullable=True, comment="Teléfono de contacto")
    website = Column(String(255), nullable=True, comment="Sitio web del proveedor")
    
    # Configuración de API
    api_config = Column(JSON, nullable=True, comment="Configuración de API en formato JSON")
    api_endpoint = Column(String(500), nullable=True, comment="Endpoint base de la API")
    api_key = Column(String(500), nullable=True, comment="API Key para autenticación")
    api_secret = Column(String(500), nullable=True, comment="API Secret para autenticación")
    api_token = Column(Text, nullable=True, comment="Token de acceso a la API")
    api_token_expires_at = Column(Text, nullable=True, 
                                  comment="Fecha de expiración del token (ISO string)")
    
    # Estado y configuración
    is_active = Column(Boolean, default=True, nullable=False, 
                       comment="Indica si el proveedor está activo")
    sync_enabled = Column(Boolean, default=False, nullable=False,
                          comment="Indica si la sincronización automática está habilitada")
    sync_frequency = Column(String(50), nullable=True, 
                            comment="Frecuencia de sincronización (daily, hourly, etc.)")
    last_sync_at = Column(Text, nullable=True, 
                          comment="Última fecha de sincronización exitosa (ISO string)")
    
    # Metadatos adicionales (no usar 'metadata' que es reservado por SQLAlchemy)
    extra_metadata = Column(JSON, nullable=True, 
                      comment="Metadatos adicionales del proveedor")
    
    # Relaciones
    # Relación uno-a-muchos con Products (se definirá en el modelo Product)
    products = relationship("Product", back_populates="supplier", 
                            cascade="all, delete-orphan",
                            lazy="dynamic")
    
    def __repr__(self):
        return f"<Supplier(id={self.id}, code='{self.code}', name='{self.name}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte el modelo a un diccionario.
        
        Returns:
            Dict[str, Any]: Diccionario con los campos del proveedor
        """
        # Usar el método to_dict de la clase base y luego extenderlo
        base_dict = super().to_dict(exclude=['api_key', 'api_secret', 'api_token'])
        # Agregar campos específicos o modificar
        base_dict.update({
            "code": self.code,
            "name": self.name,
            "contact_name": self.contact_name,
            "contact_email": self.contact_email,
            "contact_phone": self.contact_phone,
            "website": self.website,
            "is_active": self.is_active,
            "sync_enabled": self.sync_enabled,
            "sync_frequency": self.sync_frequency,
            "last_sync_at": self.last_sync_at,  # Ya es string o None
            # Nota: created_at y updated_at ya están incluidos por el método base
        })
        return base_dict
    
    def get_api_config(self) -> Dict[str, Any]:
        """
        Obtiene la configuración de API como diccionario.
        
        Returns:
            Dict[str, Any]: Configuración de API
        """
        if self.api_config:
            return self.api_config
        return {}
    
    def update_api_config(self, config: Dict[str, Any]) -> None:
        """
        Actualiza la configuración de API.
        
        Args:
            config: Nueva configuración de API
        """
        self.api_config = config
        self.update_timestamp()


# Configuración de índices adicionales
# (Se pueden agregar índices compuestos si es necesario)

