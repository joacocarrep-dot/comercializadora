
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager

# Configuración básica de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Lifespan events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up Comercializadora Digital Backend")
    yield
    # Shutdown
    logger.info("Shutting down Comercializadora Digital Backend")

# Crear aplicación FastAPI
app = FastAPI(
    title="Comercializadora Digital API",
    description="Backend para la comercializadora digital - Sistema intermediario entre proveedores y clientes",
    version="1.0.0",
    contact={
        "name": "Equipo de Desarrollo",
        "email": "dev@comercializadora.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan,
)

# Configurar CORS
# En desarrollo permitimos todos los orígenes, en producción se debe restringir
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambiar en producción a los dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint para verificar que la API está funcionando.
    """
    return {
        "status": "healthy",
        "service": "comercializadora-backend",
        "version": "1.0.0"
    }

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Endpoint raíz de la API.
    """
    return {
        "message": "Bienvenido a la API de Comercializadora Digital",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health"
    }

# Importar routers futuros aquí
# from app.api.v1 import suppliers, storefronts, products, etc.

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,  # Hot-reload para desarrollo
        log_level="info"
    )
