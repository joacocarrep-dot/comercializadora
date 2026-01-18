
# Comercializadora Digital - Backend

Backend API para la plataforma de Comercializadora Digital, construido con FastAPI, PostgreSQL, y Alembic para migraciones.

## 🚀 Características

- **API RESTful** con FastAPI
- **Autenticación JWT** con OAuth2
- **Base de datos PostgreSQL** con SQLAlchemy ORM
- **Migraciones automáticas** con Alembic
- **Docker** para contenedorización
- **Variables de entorno** con Pydantic Settings
- **Validación de datos** con Pydantic v2
- **CORS** configurado para frontend
- **Logging** estructurado
- **Pre-commit hooks** para calidad de código
- **Testing** con pytest

## 📋 Requisitos Previos

- Python 3.12+
- Docker y Docker Compose (opcional)
- PostgreSQL 15+
- Git

## 🛠️ Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/joacocarrep-dot/comercializadora.git
cd comercializadora/backend
```

### 2. Configurar entorno

```bash
# Copiar variables de entorno de ejemplo
cp .env.example .env

# Editar .env con tus valores
nano .env
```

### 3. Configurar base de datos (con Docker)

```bash
# Iniciar PostgreSQL con Docker Compose
docker compose up -d

# O instalar PostgreSQL manualmente y configurar DATABASE_URL en .env
```

### 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 5. Configurar migraciones de base de datos

```bash
# Crear migraciones iniciales
alembic upgrade head
```

### 6. Ejecutar la aplicación

```bash
# Desarrollo (con recarga automática)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Producción
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 📁 Estructura del Proyecto

```
backend/
├── app/                          # Código fuente principal
│   ├── config/                   # Configuración
│   │   └── settings.py           # Variables de entorno
│   ├── core/                     # Lógica central
│   ├── models/                   # Modelos SQLAlchemy
│   ├── schemas/                  # Esquemas Pydantic
│   ├── api/                      # Endpoints de API
│   │   ├── v1/                   # API v1
│   │   │   ├── endpoints/        # Rutas específicas
│   │   │   └── dependencies.py   # Dependencias de API
│   │   └── __init__.py
│   ├── crud/                     # Operaciones CRUD
│   ├── auth/                     # Autenticación
│   └── main.py                   # Aplicación principal
├── migrations/                   # Migraciones Alembic
├── tests/                        # Tests
├── scripts/                      # Scripts de utilidad
├── docs/                         # Documentación
├── .env.example                  # Variables de entorno ejemplo
├── .gitignore                    # Archivos ignorados por Git
├── .editorconfig                 # Configuración del editor
├── .pre-commit-config.yaml       # Hooks de pre-commit
├── docker-compose.yml            # Docker Compose
├── Dockerfile                    # Dockerfile
├── alembic.ini                   # Configuración Alembic
├── requirements.txt              # Dependencias Python
└── README.md                     # Este archivo
```

## 🔧 Configuración de Variables de Entorno

El archivo `.env.example` contiene todas las variables necesarias. Las principales son:

```env
# Entorno
ENVIRONMENT=development
DEBUG=False

# Base de datos
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/comercializadora

# Seguridad
SECRET_KEY=clave-secreta-segura-minimo-32-caracteres
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

## 🐳 Docker

### Construir y ejecutar

```bash
# Construir la imagen
docker build -t comercializadora-backend .

# Ejecutar con Docker Compose
docker compose up -d

# Ver logs
docker compose logs -f
```

### Servicios incluidos

- `postgres`: Base de datos PostgreSQL
- `backend`: Aplicación FastAPI

## 📊 Migraciones de Base de Datos

### Crear nueva migración

```bash
alembic revision --autogenerate -m "descripcion_cambios"
```

### Aplicar migraciones

```bash
# Aplicar todas las migraciones pendientes
alembic upgrade head

# Revertir última migración
alembic downgrade -1

# Ver estado de migraciones
alembic current
alembic history
```

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest

# Ejecutar tests con cobertura
pytest --cov=app tests/

# Ejecutar tests específicos
pytest tests/test_auth.py
```

## 🛡️ Seguridad

- **JWT tokens** con expiración
- **CORS** configurado
- **Validación de entrada** con Pydantic
- **SQL injection prevention** con SQLAlchemy
- **Headers de seguridad** en producción
- **Rate limiting** (pendiente de implementación)

## 🔍 Endpoints de API

### Disponibles por defecto

- `GET /` - Documentación Swagger
- `GET /docs` - Documentación interactiva (Swagger UI)
- `GET /redoc` - Documentación alternativa (ReDoc)
- `GET /health` - Health check

### Ejemplo de endpoint

```python
from fastapi import APIRouter, Depends
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/users", tags=["users"])

@router.get("/me")
async def get_current_user_info(
    current_user = Depends(get_current_user)
):
    return {"user": current_user.email, "id": current_user.id}
```

## 📝 Calidad de Código

### Pre-commit Hooks

```bash
# Instalar hooks
pre-commit install

# Ejecutar en todos los archivos
pre-commit run --all-files

# Ejecutar hook específico
pre-commit run black --all-files
```

### Herramientas incluidas

- **Black**: Formateo de código
- **isort**: Ordenación de imports
- **flake8**: Linting
- **mypy**: Chequeo de tipos
- **bandit**: Seguridad
- **safety**: Vulnerabilidades de dependencias

## 🚢 Despliegue

### Opción 1: Docker

```bash
docker build -t comercializadora-backend:latest .
docker run -p 8000:8000 --env-file .env comercializadora-backend:latest
```

### Opción 2: Servidor tradicional

```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
export $(cat .env | xargs)

# Ejecutar con gunicorn (producción)
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Opción 3: Plataformas en la nube

- **Heroku**: `Procfile` incluido
- **AWS Elastic Beanstalk**: Configuración incluida
- **Google Cloud Run**: `Dockerfile` optimizado
- **Azure App Service**: Configuración disponible

## 🤝 Contribuir

1. Fork el repositorio
2. Crear una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Añadir nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

### Convenciones de código

- Seguir PEP 8
- Usar type hints
- Escribir docstrings
- Añadir tests para nuevas funcionalidades
- Actualizar documentación

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🆘 Soporte

- **Issues**: [GitHub Issues](https://github.com/joacocarrep-dot/comercializadora/issues)
- **Email**: soporte@comercializadora.com
- **Documentación**: [Documentación completa](docs/)

## 📈 Estado del Proyecto

**Versión**: 1.0.0  
**Estado**: En desarrollo activo  
**Última actualización**: Enero 2026

---

Desarrollado con ❤️ por el equipo de Comercializadora Digital
