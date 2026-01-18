


"""
Módulo de sesión de base de datos para SQLAlchemy asíncrono.

Proporciona una fábrica de sesiones y un gestor de contexto para operaciones de base de datos.
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.config.settings import settings


# Crear motor asíncrono para PostgreSQL
engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=settings.DEBUG,  # Mostrar queries SQL en modo debug
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,  # Verificar conexiones antes de usarlas
    pool_recycle=3600,   # Reciclar conexiones cada hora
)

# Fábrica de sesiones asíncronas
AsyncSessionFactory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # No expirar objetos después del commit
    autoflush=False,         # No autoflush para mejor control
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Proveedor de dependencia para obtener una sesión de base de datos asíncrona.
    
    Yields:
        AsyncSession: Sesión de base de datos asíncrona
        
    Usage:
        async with get_session() as session:
            await session.execute(...)
    """
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


class DatabaseSessionManager:
    """
    Gestor de sesiones de base de datos para usar en middleware y otros contextos.
    
    Proporciona métodos para obtener y manejar sesiones de forma centralizada.
    """
    
    def __init__(self):
        self.engine = engine
        self.session_factory = AsyncSessionFactory
    
    async def get_session(self) -> AsyncSession:
        """
        Obtiene una nueva sesión de base de datos.
        
        Returns:
            AsyncSession: Nueva sesión de base de datos
            
        Note:
            La sesión debe ser cerrada manualmente o usada en un contexto with.
        """
        return self.session_factory()
    
    async def close(self):
        """
        Cierra el motor de base de datos.
        """
        await self.engine.dispose()


# Instancia global del gestor de sesiones
session_manager = DatabaseSessionManager()



