

"""
Modelo SQLAlchemy para Storefronts (Tiendas virtuales).
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import Column, Integer, String, Text, JSON, ForeignKey, Boolean, ARRAY, Table, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

# Importar base y mixins comunes
from app.models.base import BaseModel, Base


# Tabla de asociación para relación muchos-a-muchos entre Storefronts y Products
storefront_products = Table(
    "storefront_products",
    Base.metadata,
    Column("storefront_id", Integer, ForeignKey("storefronts.id", ondelete="CASCADE"), primary_key=True),
    Column("product_id", Integer, ForeignKey("products.id", ondelete="CASCADE"), primary_key=True),
    Column("created_at", DateTime, server_default=func.now(), nullable=False),
    Column("updated_at", DateTime, server_default=func.now(), onupdate=func.now(), nullable=False),
    Column("position", Integer, default=0, comment="Posición del producto en la tienda"),
    Column("is_featured", Boolean, default=False, comment="Producto destacado en la tienda"),
    Column("is_active", Boolean, default=True, comment="Producto activo en la tienda"),
    Column("metadata", JSON, nullable=True, comment="Metadatos adicionales de la relación"),
)


class Storefront(BaseModel):
    """
    Modelo de Storefront (Tienda virtual).
    
    Representa una tienda virtual o marketplace que vende productos a través de la plataforma.
    
    Hereda de BaseModel que ya incluye:
    - created_at, updated_at (TimestampMixin)
    - Métodos to_dict, update_from_dict, update_timestamp
    """
    __tablename__ = "storefronts"
    
    # Identificación
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String(50), unique=True, index=True, nullable=False,
                  comment="Código único de la tienda")
    name = Column(String(255), nullable=False, comment="Nombre de la tienda")
    description = Column(Text, nullable=True, comment="Descripción de la tienda")
    
    # Información de dominio y URL
    domain = Column(String(255), unique=True, nullable=True, comment="Dominio de la tienda")
    base_url = Column(String(500), nullable=True, comment="URL base de la tienda")
    
    # Configuración de API y autenticación
    api_key = Column(String(500), nullable=True, comment="API Key para integraciones")
    api_secret = Column(String(500), nullable=True, comment="API Secret para integraciones")
    webhook_url = Column(String(500), nullable=True, comment="URL para webhooks")
    webhook_secret = Column(String(500), nullable=True, comment="Secreto para validar webhooks")
    
    # Configuraciones en JSONB
    config = Column(JSON, nullable=True, default=dict, 
                    comment="Configuración general de la tienda")
    payment_config = Column(JSON, nullable=True, default=dict,
                            comment="Configuración de pagos (MercadoPago, etc.)")
    ai_config = Column(JSON, nullable=True, default=dict,
                       comment="Configuración de IA (Gemini, etc.)")
    notification_config = Column(JSON, nullable=True, default=dict,
                                 comment="Configuración de notificaciones (email, WhatsApp)")
    
    # Estado y operación
    is_active = Column(Boolean, default=True, nullable=False,
                       comment="Indica si la tienda está activa")
    is_public = Column(Boolean, default=False, nullable=False,
                       comment="Indica si la tienda es pública")
    maintenance_mode = Column(Boolean, default=False, nullable=False,
                              comment="Modo mantenimiento activo")
    
    # Categorías y etiquetas
    categories = Column(ARRAY(String), nullable=True, default=list,
                        comment="Categorías de productos de la tienda")
    tags = Column(ARRAY(String), nullable=True, default=list,
                  comment="Etiquetas de la tienda")
    
    # Información de contacto
    contact_email = Column(String(255), nullable=True, comment="Email de contacto")
    contact_phone = Column(String(50), nullable=True, comment="Teléfono de contacto")
    support_email = Column(String(255), nullable=True, comment="Email de soporte")
    
    # Metadatos adicionales (no usar 'metadata' que es reservado por SQLAlchemy)
    extra_metadata = Column(JSON, nullable=True, default=dict,
                      comment="Metadatos adicionales de la tienda")
    
    # Relaciones
    # Relación uno-a-muchos con Users (un storefront puede tener muchos usuarios)
    # Usamos string "User" para evitar importación circular
    users = relationship("User", back_populates="storefront",
                         cascade="all, delete-orphan",
                         lazy="dynamic")
    
    # Relación muchos-a-muchos con Products a través de la tabla de asociación
    # Usamos string "Product" para evitar importación circular
    products = relationship("Product",
                            secondary=storefront_products,
                            back_populates="storefronts",
                            lazy="dynamic")
    
    def __repr__(self):
        return f"<Storefront(id={self.id}, code='{self.code}', name='{self.name}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte el modelo a un diccionario.
        
        Returns:
            Dict[str, Any]: Diccionario con los campos de la tienda
        """
        # Usar el método to_dict de la clase base y luego extenderlo
        base_dict = super().to_dict(exclude=['api_key', 'api_secret', 'webhook_secret'])
        # Agregar campos específicos o modificar
        base_dict.update({
            "code": self.code,
            "name": self.name,
            "description": self.description,
            "domain": self.domain,
            "base_url": self.base_url,
            "is_active": self.is_active,
            "is_public": self.is_public,
            "maintenance_mode": self.maintenance_mode,
            "categories": self.categories,
            "tags": self.tags,
            "contact_email": self.contact_email,
            "contact_phone": self.contact_phone,
            "support_email": self.support_email,
            "config": self.config,
            "payment_config": self.payment_config,
            "ai_config": self.ai_config,
            "notification_config": self.notification_config,
            # Nota: created_at y updated_at ya están incluidos por el método base
        })
        return base_dict
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """
        Obtiene un valor de la configuración general.
        
        Args:
            key: Clave de configuración
            default: Valor por defecto si no existe
            
        Returns:
            Any: Valor de configuración
        """
        if self.config and key in self.config:
            return self.config[key]
        return default
    
    def update_config(self, key: str, value: Any) -> None:
        """
        Actualiza un valor en la configuración general.
        
        Args:
            key: Clave de configuración
            value: Nuevo valor
        """
        if self.config is None:
            self.config = {}
        self.config[key] = value
        self.update_timestamp()
    
    def get_payment_config(self) -> Dict[str, Any]:
        """
        Obtiene la configuración de pagos.
        
        Returns:
            Dict[str, Any]: Configuración de pagos
        """
        return self.payment_config if self.payment_config else {}
    
    def get_ai_config(self) -> Dict[str, Any]:
        """
        Obtiene la configuración de IA.
        
        Returns:
            Dict[str, Any]: Configuración de IA
        """
        return self.ai_config if self.ai_config else {}

