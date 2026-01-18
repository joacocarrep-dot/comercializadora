

# 🏗️ Diagrama Visual de la Estructura

## 📊 Diagrama Mermaid de la Arquitectura

```mermaid
graph TB
    %% Estructura principal
    ROOT[comercializadora-v1.0.0/backend]
    
    %% Configuración y archivos raíz
    ROOT --> CONFIG[📄 Archivos de Configuración]
    CONFIG --> ENV[.env.example]
    CONFIG --> GITIGNORE[.gitignore]
    CONFIG --> EDITORCONFIG[.editorconfig]
    CONFIG --> PRECOMMIT[.pre-commit-config.yaml]
    CONFIG --> README[README.md]
    CONFIG --> ESTRUCTURA[ESTRUCTURA.md]
    CONFIG --> DIAGRAMA[DIAGRAMA.md]
    
    %% Infraestructura
    ROOT --> INFRA[🛠️ Infraestructura]
    INFRA --> DOCKERFILE[Dockerfile]
    INFRA --> DOCKERCOMPOSE[docker-compose.yml]
    INFRA --> REQUIREMENTS[requirements.txt]
    INFRA --> ALEMBICINI[alembic.ini]
    
    %% Aplicación FastAPI
    ROOT --> APP[📁 app/ - Aplicación FastAPI]
    APP --> MAIN[main.py]
    APP --> CONFIG_DIR[📁 config/]
    CONFIG_DIR --> SETTINGS[settings.py]
    
    %% Directorios vacíos para expansión futura
    APP --> API_DIR[📁 api/]
    API_DIR --> API_V1[📁 v1/]
    API_V1 --> ENDPOINTS[📁 endpoints/]
    
    APP --> CORE_DIR[📁 core/]
    APP --> MODELS_DIR[📁 models/]
    APP --> REPOSITORIES_DIR[📁 repositories/]
    APP --> SCHEMAS_DIR[📁 schemas/]
    APP --> SERVICES_DIR[📁 services/]
    APP --> UTILS_DIR[📁 utils/]
    
    %% Migraciones
    ROOT --> MIGRATIONS[📁 migrations/]
    MIGRATIONS --> ENV_PY[env.py]
    MIGRATIONS --> SCRIPT_MAKO[script.py.mako]
    MIGRATIONS --> VERSIONS[📁 versions/]
    VERSIONS --> INITIAL_MIGRATION[a6ba16149395_initial_migration.py]
    
    %% Otros directorios
    ROOT --> DOCS[📁 docs/]
    ROOT --> SCRIPTS[📁 scripts/]
    ROOT --> TESTS[📁 tests/]
```

## 🔄 Diagrama de Flujo de Configuración

```mermaid
flowchart TD
    START[Inicio del Proyecto] --> CLONAR[Clonar repositorio]
    CLONAR --> ENV_CONFIG[Configurar entorno]
    ENV_CONFIG --> ENV_COPY[Copiar .env.example a .env]
    ENV_COPY --> ENV_EDIT[Editar variables en .env]
    
    ENV_EDIT --> DB_SETUP[Configurar base de datos]
    DB_SETUP --> DOCKER_OPTION{Usar Docker?}
    DOCKER_OPTION -->|Sí| DOCKER_COMPOSE[docker compose up -d]
    DOCKER_OPTION -->|No| MANUAL_DB[Configurar PostgreSQL manualmente]
    
    DOCKER_COMPOSE --> INSTALL_DEPS[Instalar dependencias]
    MANUAL_DB --> INSTALL_DEPS
    
    INSTALL_DEPS --> MIGRATIONS[Aplicar migraciones]
    MIGRATIONS --> ALEMBIC_INIT[alembic upgrade head]
    
    ALEMBIC_INIT --> RUN_APP[Ejecutar aplicación]
    RUN_APP --> DEV_MODE{Modo desarrollo?}
    DEV_MODE -->|Sí| UVICORN_DEV[uvicorn app.main:app --reload]
    DEV_MODE -->|No| UVICORN_PROD[uvicorn app.main:app]
    
    UVICORN_DEV --> API_READY[API lista en http://localhost:8000]
    UVICORN_PROD --> API_READY
    
    API_READY --> DOCS[Documentación en /docs y /redoc]
    DOCS --> HEALTH_CHECK[Health check en /health]
```

## 🏗️ Diagrama de Clases (Settings)

```mermaid
classDiagram
    class Settings {
        <<Pydantic BaseSettings>>
        -ENVIRONMENT: str
        -DEBUG: bool
        -DATABASE_URL: PostgresDsn
        -DATABASE_POOL_SIZE: int
        -DATABASE_MAX_OVERFLOW: int
        -SECRET_KEY: str
        -ALGORITHM: str
        -ACCESS_TOKEN_EXPIRE_MINUTES: int
        -REFRESH_TOKEN_EXPIRE_DAYS: int
        -ALLOWED_ORIGINS: List[str]
        -ALLOWED_METHODS: List[str]
        -ALLOWED_HEADERS: List[str]
        -LOG_LEVEL: str
        -LOG_FORMAT: str
        -MERCADOPAGO_ACCESS_TOKEN: Optional[str]
        -MERCADOPAGO_PUBLIC_KEY: Optional[str]
        -GEMINI_API_KEY: Optional[str]
        -WHATSAPP_API_TOKEN: Optional[str]
        -SENDGRID_API_KEY: Optional[str]
        -TWILIO_ACCOUNT_SID: Optional[str]
        -TWILIO_AUTH_TOKEN: Optional[str]
        -TWILIO_PHONE_NUMBER: Optional[str]
        -APP_NAME: str
        -APP_VERSION: str
        -API_PREFIX: str
        -REQUEST_TIMEOUT: int
        -MAX_UPLOAD_SIZE: int
        -REDIS_URL: Optional[str]
        +validate_environment(cls, v) str
        +validate_database_url(cls, v) str
        +parse_allowed_origins(cls, v) List[str]
        +Config
    }
    
    class Config {
        -env_file: str = ".env"
        -env_file_encoding: str = "utf-8"
        -case_sensitive: bool = False
        -extra: str = "ignore"
    }
    
    Settings "1" *-- "1" Config : contiene
```

## 🔗 Dependencias y Relaciones

```mermaid
graph LR
    %% Núcleo de la aplicación
    FASTAPI[FastAPI] --> UVICORN[Uvicorn]
    FASTAPI --> SQLALCHEMY[SQLAlchemy]
    FASTAPI --> PYDANTIC[Pydantic]
    
    %% Configuración
    PYDANTIC --> PYDANTIC_SETTINGS[Pydantic Settings]
    PYDANTIC_SETTINGS --> DOTENV[python-dotenv]
    
    %% Base de datos
    SQLALCHEMY --> ALEMBIC[Alembic]
    SQLALCHEMY --> ASYNCPG[asyncpg]
    ASYNCPG --> POSTGRESQL[PostgreSQL]
    
    %% Seguridad
    FASTAPI --> PYTHON_JOSE[python-jose]
    PYTHON_JOSE --> CRYPTOGRAPHY[Cryptography]
    
    %% Calidad de código
    PROJECT[Proyecto] --> PRE_COMMIT[pre-commit]
    PRE_COMMIT --> BLACK[black]
    PRE_COMMIT --> ISORT[isort]
    PRE_COMMIT --> FLAKE8[flake8]
    PRE_COMMIT --> MYPY[mypy]
    PRE_COMMIT --> BANDIT[bandit]
    
    %% Utilidades
    PROJECT --> REQUESTS[requests]
    PROJECT --> HTTPX[httpx]
    PROJECT --> PYTEST[pytest]
    
    %% Estilos y relaciones
    style FASTAPI fill:#e1f5fe
    style SQLALCHEMY fill:#f3e5f5
    style PYDANTIC fill:#e8f5e8
    style POSTGRESQL fill:#fff3e0
    style PRE_COMMIT fill:#ffebee
```

## 📁 Estructura Jerárquica Detallada

```
comercializadora-v1.0.0/backend/
│
├── 📄 .editorconfig
├── 📄 .env.example
├── 📄 .gitignore
├── 📄 .pre-commit-config.yaml
├── 📄 Dockerfile
├── 📄 README.md
├── 📄 ESTRUCTURA.md
├── 📄 DIAGRAMA.md
├── 📄 alembic.ini
├── 📄 docker-compose.yml
├── 📄 requirements.txt
│
├── 📁 app/
│   ├── 📄 main.py
│   │
│   ├── 📁 api/
│   │   └── 📁 v1/
│   │       ├── 📁 endpoints/      # ← Futuros endpoints
│   │       │   ├── 📄 auth.py
│   │       │   ├── 📄 users.py
│   │       │   ├── 📄 products.py
│   │       │   └── 📄 orders.py
│   │       └── 📄 __init__.py
│   │
│   ├── 📁 config/
│   │   └── 📄 settings.py        # ⭐ Configuración principal
│   │
│   ├── 📁 core/                  # ← Futura lógica central
│   ├── 📁 models/                # ← Futuros modelos SQLAlchemy
│   ├── 📁 repositories/          # ← Futuro acceso a datos
│   ├── 📁 schemas/               # ← Futuros esquemas Pydantic
│   ├── 📁 services/              # ← Futura lógica de negocio
│   └── 📁 utils/                 # ← Futuras utilidades
│
├── 📁 docs/                      # ← Futura documentación
│
├── 📁 migrations/                # ✅ Migraciones configuradas
│   ├── 📄 env.py
│   ├── 📄 script.py.mako
│   ├── 📄 README
│   └── 📁 versions/
│       └── 📄 a6ba16149395_initial_migration.py
│
├── 📁 scripts/                   # ← Futuros scripts
│
└── 📁 tests/                     # ← Futuros tests
    ├── 📄 conftest.py
    ├── 📁 test_api/
    ├── 📁 test_models/
    └── 📁 test_services/
```

## 🎨 Leyenda de Símbolos

| Símbolo | Significado |
|---------|-------------|
| 📁 | Directorio |
| 📄 | Archivo |
| ⭐ | Archivo clave |
| ✅ | Configurado/completado |
| ← | Para desarrollo futuro |
| 🔄 | Flujo/proceso |
| 🏗️ | Estructura/arquitectura |
| 📊 | Diagrama/visualización |

## 📈 Evolución del Proyecto

```mermaid
timeline
    title Evolución del Backend
    section Fase 1: Configuración Inicial
        Enero 2026 : Setup inicial<br>FastAPI + PostgreSQL
        : Variables de entorno<br>y settings
        : Git configurado<br>con pre-commit hooks
    
    section Fase 2: Desarrollo Core
        Próximos pasos : Modelos de datos<br>y migraciones
        : Autenticación JWT<br>y seguridad
        : Endpoints CRUD<br>básicos
    
    section Fase 3: Integraciones
        Futuro : Integración con<br>MercadoPago
        : Integración con<br>WhatsApp API
        : Integración con<br>Google Gemini AI
    
    section Fase 4: Producción
        Despliegue : Docker optimizado<br>para producción
        : Monitoring<br>y logging
        : Escalabilidad<br>y performance
```

---

**Visualización creada**: Enero 2026  
**Herramientas**: Mermaid.js, Markdown  
**Propósito**: Documentación visual de la arquitectura  
**Estado**: Configuración inicial completada ✅

