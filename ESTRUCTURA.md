

# 📁 Diagrama de Estructura del Proyecto

## 🌳 Estructura General del Backend

```
comercializadora-v1.0.0/backend/
├── 📁 app/                          # Aplicación principal FastAPI
│   ├── 📁 api/                      # Endpoints de API
│   │   └── 📁 v1/                   # Versión 1 de la API
│   │       ├── 📁 endpoints/        # Rutas específicas (vacío)
│   │       └── 📄 __init__.py       # Inicialización del módulo
│   ├── 📁 config/                   # Configuración
│   │   └── 📄 settings.py           # Variables de entorno (Pydantic Settings)
│   ├── 📁 core/                     # Lógica central (vacío)
│   ├── 📁 models/                   # Modelos SQLAlchemy (vacío)
│   ├── 📁 repositories/             # Acceso a datos (vacío)
│   ├── 📁 schemas/                  # Esquemas Pydantic (vacío)
│   ├── 📁 services/                 # Lógica de negocio (vacío)
│   ├── 📁 utils/                    # Utilidades (vacío)
│   └── 📄 main.py                   # Aplicación FastAPI principal
│
├── 📁 docs/                         # Documentación (vacío)
├── 📁 migrations/                   # Migraciones de base de datos (Alembic)
│   ├── 📁 versions/                 # Migraciones versionadas
│   │   ├── 📄 a6ba16149395_initial_migration.py
│   │   └── 📁 __pycache__/
│   ├── 📄 env.py                    # Configuración de entorno Alembic
│   ├── 📄 script.py.mako            # Template para migraciones
│   └── 📄 README                    # Documentación de Alembic
│
├── 📁 scripts/                      # Scripts de utilidad (vacío)
├── 📁 tests/                        # Tests (vacío)
│
├── 📄 .editorconfig                 # Configuración de estilo del editor
├── 📄 .env.example                  # Variables de entorno de ejemplo
├── 📄 .gitignore                    # Archivos ignorados por Git
├── 📄 .pre-commit-config.yaml       # Configuración de hooks de pre-commit
├── 📄 Dockerfile                    # Docker para la aplicación
├── 📄 README.md                     # Documentación principal
├── 📄 alembic.ini                   # Configuración de Alembic
├── 📄 docker-compose.yml            # Docker Compose (PostgreSQL)
├── 📄 requirements.txt              # Dependencias Python
└── 📄 ESTRUCTURA.md                 # Este archivo
```

## 📊 Diagrama de Clases

### 🏗️ Clase Principal: `Settings` (en `app/config/settings.py`)

```
┌─────────────────────────────────────────────────────────────┐
│                      Settings (Pydantic)                    │
├─────────────────────────────────────────────────────────────┤
│ - ENVIRONMENT: str = "development"                          │
│ - DEBUG: bool = False                                       │
│ - DATABASE_URL: PostgresDsn                                │
│ - DATABASE_POOL_SIZE: int = 5                              │
│ - DATABASE_MAX_OVERFLOW: int = 10                          │
│ - SECRET_KEY: str                                          │
│ - ALGORITHM: str = "HS256"                                 │
│ - ACCESS_TOKEN_EXPIRE_MINUTES: int = 30                    │
│ - REFRESH_TOKEN_EXPIRE_DAYS: int = 7                       │
│ - ALLOWED_ORIGINS: List[str]                               │
│ - ALLOWED_METHODS: List[str]                               │
│ - ALLOWED_HEADERS: List[str]                               │
│ - LOG_LEVEL: str = "INFO"                                  │
│ - LOG_FORMAT: str                                          │
│ - MERCADOPAGO_ACCESS_TOKEN: Optional[str]                  │
│ - MERCADOPAGO_PUBLIC_KEY: Optional[str]                    │
│ - GEMINI_API_KEY: Optional[str]                            │
│ - WHATSAPP_API_TOKEN: Optional[str]                        │
│ - SENDGRID_API_KEY: Optional[str]                          │
│ - TWILIO_ACCOUNT_SID: Optional[str]                        │
│ - TWILIO_AUTH_TOKEN: Optional[str]                         │
│ - TWILIO_PHONE_NUMBER: Optional[str]                       │
│ - APP_NAME: str = "Comercializadora Digital"               │
│ - APP_VERSION: str = "1.0.0"                               │
│ - API_PREFIX: str = "/api/v1"                              │
│ - REQUEST_TIMEOUT: int = 30                                │
│ - MAX_UPLOAD_SIZE: int = 10485760                          │
│ - REDIS_URL: Optional[str]                                 │
├─────────────────────────────────────────────────────────────┤
│ + validate_environment(cls, v) -> str                      │
│ + validate_database_url(cls, v) -> str                     │
│ + parse_allowed_origins(cls, v) -> List[str]               │
├─────────────────────────────────────────────────────────────┤
│ Config:                                                    │
│   env_file = ".env"                                        │
│   env_file_encoding = "utf-8"                              │
│   case_sensitive = False                                   │
│   extra = "ignore"                                         │
└─────────────────────────────────────────────────────────────┘
```

### 🔄 Relaciones y Dependencias

```
┌─────────────────┐    usa     ┌─────────────────┐
│   FastAPI App   │───────────▶│    Settings     │
│   (main.py)     │            │  (settings.py)  │
└─────────────────┘            └─────────────────┘
         │                              │
         │ usa                          │ configura
         ▼                              ▼
┌─────────────────┐            ┌─────────────────┐
│   PostgreSQL    │            │   Variables     │
│   (Docker)      │            │   de Entorno    │
└─────────────────┘            │   (.env/.env.example) │
         │                     └─────────────────┘
         │ usa
         ▼
┌─────────────────┐
│     Alembic     │
│  (migraciones)  │
└─────────────────┘
```

## 📋 Archivos Clave y su Propósito

### **Configuración y Entorno**
| Archivo | Propósito |
|---------|-----------|
| `.env.example` | Plantilla con todas las variables de entorno necesarias |
| `app/config/settings.py` | Configuración de la aplicación usando Pydantic Settings |
| `.gitignore` | Archivos y directorios excluidos del control de versiones |
| `.editorconfig` | Estándares de formato para diferentes editores |
| `.pre-commit-config.yaml` | Hooks para calidad de código antes de commits |

### **Infraestructura**
| Archivo | Propósito |
|---------|-----------|
| `Dockerfile` | Contenedorización de la aplicación |
| `docker-compose.yml` | Orquestación con PostgreSQL |
| `alembic.ini` | Configuración de migraciones de base de datos |
| `requirements.txt` | Dependencias de Python |

### **Código Fuente**
| Archivo | Propósito |
|---------|-----------|
| `app/main.py` | Punto de entrada de la aplicación FastAPI |
| `app/config/settings.py` | Gestión de configuración y variables |
| `migrations/env.py` | Configuración de entorno de Alembic |
| `migrations/versions/*.py` | Migraciones específicas de la base de datos |

### **Documentación**
| Archivo | Propósito |
|---------|-----------|
| `README.md` | Documentación principal del proyecto |
| `ESTRUCTURA.md` | Este diagrama de estructura |
| `migrations/README` | Documentación de Alembic |

## 🗂️ Directorios para Expansión Futura

### **Directorio `app/` - Estructura planeada:**
```
app/
├── api/                           # Endpoints HTTP
│   └── v1/                        # API v1
│       ├── endpoints/             # Rutas agrupadas por dominio
│       │   ├── auth.py            # Autenticación
│       │   ├── users.py           # Usuarios
│       │   ├── products.py        # Productos
│       │   └── orders.py          # Pedidos
│       └── dependencies.py        # Dependencias de API
│
├── core/                          # Lógica central
│   ├── security.py                # Seguridad, JWT
│   ├── database.py                # Conexión a base de datos
│   └── config.py                  # Configuración extendida
│
├── models/                        # Modelos SQLAlchemy
│   ├── user.py                    # Modelo Usuario
│   ├── product.py                 # Modelo Producto
│   └── order.py                   # Modelo Pedido
│
├── schemas/                       # Esquemas Pydantic
│   ├── user.py                    # Esquemas Usuario
│   ├── product.py                 # Esquemas Producto
│   └── order.py                   # Esquemas Pedido
│
├── crud/                          # Operaciones CRUD
│   ├── user.py                    # CRUD Usuario
│   ├── product.py                 # CRUD Producto
│   └── order.py                   # CRUD Pedido
│
├── services/                      # Lógica de negocio
│   ├── auth_service.py            # Servicio de autenticación
│   ├── payment_service.py         # Servicio de pagos
│   └── notification_service.py    # Servicio de notificaciones
│
└── utils/                         # Utilidades
    ├── validators.py              # Validadores personalizados
    └── helpers.py                 # Funciones helper
```

### **Directorio `tests/` - Estructura planeada:**
```
tests/
├── conftest.py                    # Configuración de pytest
├── test_api/                      # Tests de API
│   ├── test_auth.py               # Tests de autenticación
│   ├── test_users.py              # Tests de usuarios
│   └── test_products.py           # Tests de productos
│
├── test_models/                   # Tests de modelos
├── test_services/                 # Tests de servicios
└── test_utils/                    # Tests de utilidades
```

## 🔗 Dependencias del Proyecto

### **Principales (requirements.txt):**
```
fastapi==0.104.1           # Framework web
uvicorn[standard]==0.24.0  # Servidor ASGI
sqlalchemy==2.0.23         # ORM para PostgreSQL
alembic==1.13.1            # Migraciones de base de datos
asyncpg==0.29.0            # Driver async para PostgreSQL
pydantic==2.5.0            # Validación de datos
pydantic-settings==2.1.0   # Gestión de configuración
python-jose[cryptography]==3.3.0  # JWT tokens
```

## 🚀 Flujo de Desarrollo

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Código    │───▶│  Pre-commit │───▶│     Git     │
│   Fuente    │    │    Hooks    │    │   Commit    │
└─────────────┘    └─────────────┘    └─────────────┘
        │                  │                  │
        ▼                  ▼                  ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Alembic   │    │    Tests    │    │    Push     │
│ Migraciones │    │   (pytest)  │    │  a Remote   │
└─────────────┘    └─────────────┘    └─────────────┘
        │                  │                  │
        ▼                  ▼                  ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Docker    │    │    CI/CD     │    │  Pull       │
│   Build     │    │  Pipeline    │    │  Request    │
└─────────────┘    └─────────────┘    └─────────────┘
```

## 📊 Estadísticas del Proyecto

- **Total de archivos**: 12 archivos principales
- **Total de directorios**: 15 directorios principales
- **Líneas de código Python**: ~300 líneas (estimado)
- **Clases principales**: 1 (Settings)
- **Dependencias**: 8 paquetes principales
- **Branches Git**: 3 (main, develop, feature-comercializadora)

---

**Última actualización**: Enero 2026  
**Versión del proyecto**: 1.0.0  
**Estado**: Configuración inicial completada, listo para desarrollo

