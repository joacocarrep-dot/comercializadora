# Requisitos de Pruebas - Comercializadora Digital Backend

## Resumen de Implementación

### Arquitectura Implementada
- **Framework**: FastAPI con Python 3.10+
- **Base de datos**: PostgreSQL (SQLite para desarrollo)
- **Autenticación**: JWT (JSON Web Tokens) con Bearer tokens
- **Middlewares**: Storefront identification, Request logging, Error handling
- **Estructura**: Arquitectura por capas (models, repositories, schemas, API)

### Componentes Principales

#### 1. Middleware Core
- **StorefrontMiddleware**: Identifica tiendas mediante headers `X-Storefront-Code` y `X-API-Key`
- **RequestLoggingMiddleware**: Logs estructurados en formato JSON para todas las peticiones
- **ErrorHandlingMiddleware**: Manejo centralizado de excepciones con respuestas estandarizadas

#### 2. Sistema de Autenticación JWT
- **Módulo**: `app/core/security.py`
- **Funciones**: `create_access_token()`, `verify_password()`, `get_password_hash()`
- **Dependencias**: `get_current_user()`, `require_admin()`
- **Algoritmo**: HS256 con SECRET_KEY configurable

#### 3. API Admin - CRUD Operations
- **Suppliers**: Proveedores externos de productos
- **Storefronts**: Tiendas virtuales con API Key automática

#### 4. Repositorios y Modelos
- **Modelos Base**: `BaseModel` con timestamps y métodos comunes
- **Repositorios**: Patrón Repository para abstracción de datos
- **Schemas Pydantic**: Validación y serialización de datos

---

## Estrategia de Pruebas

### Tipos de Pruebas
1. **Pruebas de integración**: API endpoints con base de datos real
2. **Pruebas de autenticación**: Flujos JWT y autorización
3. **Pruebas de middleware**: Comportamiento de middlewares
4. **Pruebas de validación**: Schemas Pydantic y reglas de negocio

### Entorno de Pruebas
- **Base de datos**: SQLite en memoria para pruebas
- **Servidor**: Uvicorn en puerto de prueba (8000+)
- **Herramientas**: pytest, httpx, alembic para migraciones

---

## Plan de Pruebas Paso a Paso

### Fase 1: Configuración del Entorno
#### Objetivo: Verificar que el entorno está listo para pruebas

**Prueba 1.1 - Verificar estructura del proyecto**
```
Input: N/A (verificación automática)
Acción: Verificar que existen directorios críticos
Output Esperado:
- Directorio /app existe con subdirectorios: api, core, models, repositories, schemas
- Archivo requirements.txt contiene todas las dependencias
- Archivo alembic.ini configurado correctamente
```

**Prueba 1.2 - Instalar dependencias**
```
Input: requirements.txt
Acción: pip install -r requirements.txt
Output Esperado:
- Todas las dependencias instaladas sin errores
- Versiones compatibles instaladas
- No hay conflictos de dependencias
```

**Prueba 1.3 - Configurar variables de entorno**
```
Input: .env.example
Acción: Copiar a .env y configurar valores
Output Esperado:
- Archivo .env creado con variables requeridas:
  * DATABASE_URL (ej: sqlite:///./test.db)
  * SECRET_KEY (32+ caracteres aleatorios)
  * ENVIRONMENT=testing
- Variables accesibles desde settings.py
```

**Prueba 1.4 - Ejecutar migraciones de base de datos**
```
Input: Alembic migrations
Acción: alembic upgrade head
Output Esperado:
- Tablas creadas en base de datos:
  * users
  * suppliers  
  * storefronts
  * storefront_products (tabla de asociación)
- No errores durante migración
- Timestamps y constraints aplicados
```

### Fase 2: Datos Iniciales y Usuarios
#### Objetivo: Crear datos de prueba y usuario administrador

**Prueba 2.1 - Crear usuario administrador inicial**
```
Input: Datos de usuario admin
Acción: Script para crear usuario en base de datos
Output Esperado:
- Usuario creado en tabla users con:
  * email: admin@comercializadora.com
  * hashed_password: hash de contraseña segura
  * role: admin
  * is_active: True
- Password hasheado con bcrypt
- Usuario accesible vía UserRepository
```

**Prueba 2.2 - Verificar conexión a base de datos**
```
Input: Configuración DATABASE_URL
Acción: Establecer conexión y ejecutar consulta simple
Output Esperado:
- Conexión exitosa a base de datos
- Query SELECT 1 devuelve resultado
- Session factory funcionando correctamente
```

### Fase 3: Inicio del Servidor y Salud API
#### Objetivo: Verificar que el servidor inicia correctamente

**Prueba 3.1 - Iniciar servidor FastAPI**
```
Input: Comando uvicorn
Acción: uvicorn app.main:app --host 0.0.0.0 --port 8000
Output Esperado:
- Servidor inicia sin errores
- Log: "Application startup complete"
- Middlewares registrados correctamente
- Routers montados: /api/v1/*
```

**Prueba 3.2 - Verificar endpoints de salud**
```
Input: GET request a /health
Acción: curl http://localhost:8000/health
Output Esperado:
- Status code: 200 OK
- Response body: {"status": "healthy", "timestamp": "..."}
- Response headers incluyen Content-Type: application/json
```

**Prueba 3.3 - Verificar documentación Swagger**
```
Input: GET request a /docs
Acción: Navegar a http://localhost:8000/docs
Output Esperado:
- Interfaz Swagger UI cargada correctamente
- Todos los endpoints documentados
- Schemas Pydantic visibles en documentación
- Ejemplos de requests disponibles
```

### Fase 4: Pruebas de Autenticación JWT
#### Objetivo: Verificar flujo completo de autenticación

**Prueba 4.1 - Login exitoso (usuario administrador)**
```
Input (Request):
POST /api/v1/auth/login
Content-Type: application/json
Body: {"email": "admin@comercializadora.com", "password": "Admin123!"}

Output Esperado:
- Status code: 200 OK
- Response body incluye:
  * access_token (JWT válido)
  * token_type: "bearer"
  * expires_in: segundos hasta expiración
- Token contiene claims:
  * sub: email del usuario
  * role: "admin"
  * exp: timestamp de expiración
```

**Prueba 4.2 - Login fallido (credenciales incorrectas)**
```
Input (Request):
POST /api/v1/auth/login
Body: {"email": "admin@comercializadora.com", "password": "wrongpassword"}

Output Esperado:
- Status code: 401 Unauthorized
- Response body: {"detail": "Credenciales inválidas"}
- No se genera token JWT
```

**Prueba 4.3 - Acceso a endpoint protegido sin token**
```
Input (Request):
GET /api/v1/admin/suppliers
Sin header Authorization

Output Esperado:
- Status code: 401 Unauthorized
- Response body: {"detail": "No autenticado"}
- Log de request incluye intento no autenticado
```

**Prueba 4.4 - Acceso a endpoint admin con usuario no-admin**
```
Input (Request):
GET /api/v1/admin/suppliers
Authorization: Bearer <token_de_usuario_no_admin>

Output Esperado:
- Status code: 403 Forbidden
- Response body: {"detail": "Permisos insuficientes"}
- Log incluye intento de acceso no autorizado
```

### Fase 5: Pruebas de Middleware
#### Objetivo: Verificar comportamiento de middlewares

**Prueba 5.1 - StorefrontMiddleware: Identificación exitosa**
```
Input (Request):
GET /api/v1/products
Headers:
  X-Storefront-Code: tienda-prueba
  X-API-Key: sf_abcdef1234567890

Output Esperado:
- Status code: 200 OK o 404 si no hay productos
- Request.state.storefront contiene objeto storefront
- Log incluye storefront_id identificado
- Headers procesados correctamente
```

**Prueba 5.2 - StorefrontMiddleware: API Key inválida**
```
Input (Request):
GET /api/v1/products
Headers:
  X-Storefront-Code: tienda-prueba
  X-API-Key: clave-invalida

Output Esperado:
- Status code: 401 Unauthorized
- Response body: {"detail": "API Key inválida"}
- Log incluye intento de acceso con API Key inválida
- Storefront no identificado en request.state
```

**Prueba 5.3 - RequestLoggingMiddleware: Logs estructurados**
```
Input (Request):
Cualquier endpoint accedido

Output Esperado:
- Log en formato JSON con campos:
  * timestamp
  * level: INFO/ERROR
  * method: GET/POST/etc
  * path: /api/v1/...
  * status_code: 200/404/etc
  * duration_ms: tiempo de procesamiento
  * storefront_id: si está identificado
  * user_id: si está autenticado
- Logs escritos en stdout o archivo configurado
```

**Prueba 5.4 - ErrorHandlingMiddleware: Excepción controlada**
```
Input (Request):
GET /api/v1/admin/suppliers/9999 (ID inexistente)

Output Esperado:
- Status code: 404 Not Found
- Response body estandarizada:
  {
    "error": "Recurso no encontrado",
    "detail": "Supplier con ID 9999 no encontrado",
    "status_code": 404
  }
- Log incluye el error con stack trace (si DEBUG=true)
```

### Fase 6: Pruebas API Admin - Suppliers
#### Objetivo: Verificar CRUD completo de proveedores

**Prueba 6.1 - Crear supplier exitosamente**
```
Input (Request):
POST /api/v1/admin/suppliers
Authorization: Bearer <token_admin>
Body: {
  "code": "proveedor-test",
  "name": "Proveedor de Prueba S.A.",
  "contact_email": "contacto@proveedortest.com",
  "is_active": true,
  "sync_enabled": false
}

Output Esperado:
- Status code: 201 Created
- Response body incluye:
  * id: número generado
  * code: "proveedor-test"
  * created_at: timestamp
  * updated_at: timestamp
  * Campos del request preservados
- Supplier creado en base de datos
- No incluye campos sensibles (api_key, api_secret)
```

**Prueba 6.2 - Crear supplier con código duplicado**
```
Input (Request):
POST /api/v1/admin/suppliers
Body: {"code": "proveedor-test", "name": "Otro Proveedor"}

Output Esperado:
- Status code: 409 Conflict
- Response body: {"detail": "Supplier con código 'proveedor-test' ya existe"}
- No se crea supplier duplicado
```

**Prueba 6.3 - Listar suppliers con paginación**
```
Input (Request):
GET /api/v1/admin/suppliers?page=1&page_size=10

Output Esperado:
- Status code: 200 OK
- Response body:
  {
    "items": [array de suppliers],
    "total": 15,
    "page": 1,
    "page_size": 10,
    "total_pages": 2
  }
- Items ordenados por created_at descendente
- Campos sensibles excluidos de la respuesta
```

**Prueba 6.4 - Obtener supplier por ID**
```
Input (Request):
GET /api/v1/admin/suppliers/1

Output Esperado:
- Status code: 200 OK
- Response body: objeto supplier completo (sin campos sensibles)
- Incluye timestamps y relaciones si aplica
```

**Prueba 6.5 - Actualizar supplier**
```
Input (Request):
PUT /api/v1/admin/suppliers/1
Body: {"name": "Nombre Actualizado", "is_active": false}

Output Esperado:
- Status code: 200 OK
- Response body: supplier actualizado
- updated_at cambiado a timestamp actual
- Campos no especificados preservan su valor
```

**Prueba 6.6 - Eliminar supplier sin productos**
```
Input (Request):
DELETE /api/v1/admin/suppliers/1

Output Esperado:
- Status code: 204 No Content
- Supplier eliminado de base de datos
- Response body vacío
```

**Prueba 6.7 - Eliminar supplier con productos (debe fallar)**
```
Input (Request):
DELETE /api/v1/admin/suppliers/1 (con productos asociados)

Output Esperado:
- Status code: 409 Conflict
- Response body: {"detail": "No se puede eliminar supplier con productos asociados"}
- Supplier no eliminado
```

### Fase 7: Pruebas API Admin - Storefronts
#### Objetivo: Verificar CRUD de tiendas con API Key automática

**Prueba 7.1 - Crear storefront con API Key generada**
```
Input (Request):
POST /api/v1/admin/storefronts
Body: {
  "code": "tienda-test",
  "name": "Tienda de Prueba",
  "domain": "tiendatest.com",
  "is_active": true,
  "is_public": true
}

Output Esperado:
- Status code: 201 Created
- Response body incluye:
  * id: número generado
  * code: "tienda-test"
  * api_key_exists: true
  * created_at, updated_at
- API Key generada automáticamente (prefijo "sf_")
- API Secret generado y almacenado
- Webhook secret generado si hay webhook_url
```

**Prueba 7.2 - Crear storefront con API Key personalizada**
```
Input (Request):
POST /api/v1/admin/storefronts
Body: {
  "code": "tienda-personalizada",
  "name": "Tienda Personalizada",
  "api_key": "custom_key_123"
}

Output Esperado:
- Status code: 201 Created
- Response body con api_key_exists: true
- API Key usada: "custom_key_123"
- API Secret generado automáticamente
```

**Prueba 7.3 - Generar nueva API Key para storefront existente**
```
Input (Request):
POST /api/v1/admin/storefronts/1/api-keys
Body: {"key_name": "Clave para integración ERP"}

Output Esperado:
- Status code: 201 Created
- Response body incluye:
  * api_key: nueva clave generada
  * api_key_id: identificador único
  * key_name: "Clave para integración ERP"
  * created_at, expires_at
- API Key anterior invalidada
- Nueva clave almacenada en storefront
```

**Prueba 7.4 - Activar modo mantenimiento**
```
Input (Request):
POST /api/v1/admin/storefronts/1/maintenance?enable=true

Output Esperado:
- Status code: 200 OK
- Response body con maintenance_mode: true
- Storefront en modo mantenimiento
- Acceso público restringido (dependiendo de implementación)
```

**Prueba 7.5 - Listar storefronts con filtros**
```
Input (Request):
GET /api/v1/admin/storefronts?is_active=true&is_public=true

Output Esperado:
- Status code: 200 OK
- Response body paginada
- Solo storefronts activos y públicos
- Campos sensibles excluidos (api_key, api_secret, webhook_secret)
```

### Fase 8: Pruebas de Validación y Esquemas
#### Objetivo: Verificar validación de datos con Pydantic

**Prueba 8.1 - Validación de email inválido**
```
Input (Request):
POST /api/v1/admin/suppliers
Body: {"code": "test", "name": "Test", "contact_email": "email-invalido"}

Output Esperado:
- Status code: 422 Unprocessable Entity
- Response body con detalles de validación:
  {
    "detail": [
      {
        "loc": ["body", "contact_email"],
        "msg": "Email inválido",
        "type": "value_error"
      }
    ]
  }
```

**Prueba 8.2 - Validación de código con caracteres inválidos**
```
Input (Request):
POST /api/v1/admin/storefronts
Body: {"code": "tienda@test", "name": "Test"}

Output Esperado:
- Status code: 422 Unprocessable Entity
- Error: "El código solo puede contener letras, números, guiones y guiones bajos"
```

**Prueba 8.3 - Validación de dominio inválido**
```
Input (Request):
POST /api/v1/admin/storefronts
Body: {"code": "test", "name": "Test", "domain": "dominio invalido"}

Output Esperado:
- Status code: 422 Unprocessable Entity
- Error: "Formato de dominio inválido"
```

### Fase 9: Pruebas de Rendimiento y Límites
#### Objetivo: Verificar comportamiento bajo carga y límites

**Prueba 9.1 - Paginación con límites**
```
Input (Request):
GET /api/v1/admin/suppliers?page_size=150 (más allá del límite)

Output Esperado:
- Status code: 422 Unprocessable Entity o 200 con page_size limitado
- Límite aplicado: máximo 100 items por página
- Mensaje de error apropiado si se excede límite
```

**Prueba 9.2 - Rate limiting básico (si implementado)**
```
Input (Request):
Múltiples requests rápidos al mismo endpoint

Output Esperado:
- Primeras requests: 200 OK
- Después de límite: 429 Too Many Requests
- Header Retry-After indicando tiempo de espera
```

### Fase 10: Pruebas de Integración Completa
#### Objetivo: Flujos completos de usuario real

**Prueba 10.1 - Flujo completo: Admin crea storefront y asigna usuario**
```
Pasos:
1. Login como admin → Obtener token
2. Crear storefront → Obtener API Key
3. Crear usuario para storefront
4. Login usuario storefront
5. Acceder recursos de storefront

Output Esperado:
- Todos los pasos exitosos (2xx status codes)
- Usuario asociado correctamente a storefront
- Permisos aplicados correctamente
- Logs muestran todo el flujo
```

**Prueba 10.2 - Flujo completo: Supplier con sincronización**
```
Pasos:
1. Crear supplier con API credentials
2. Configurar sync_enabled: true
3. Ejecutar sincronización manual
4. Verificar productos sincronizados

Output Esperado:
- Supplier creado con credenciales
- Sync endpoint inicia sincronización
- Products creados/actualizados en DB
- last_sync_at actualizado
```

---

## Criterios de Aceptación

### Éxito General
- ✅ Todas las fases 1-3 completadas sin errores
- ✅ Autenticación JWT funcionando (fase 4)
- ✅ CRUD operations exitosas (fases 6-7)
- ✅ Validación y middlewares funcionando (fases 5,8)
- ✅ Flujos de integración completos (fase 10)

### Métricas de Calidad
- **Cobertura de código**: >80% en componentes críticos
- **Tiempo de respuesta**: <500ms para operaciones CRUD
- **Tasa de errores**: <1% en pruebas automatizadas
- **Consistencia de datos**: 100% de operaciones ACID

### Requisitos No Funcionales
- **Seguridad**: No exposición de datos sensibles en logs/respuestas
- **Escalabilidad**: Soporte para 100+ storefronts concurrentes
- **Mantenibilidad**: Logs estructurados para debugging
- **Documentación**: OpenAPI/Swagger actualizado automáticamente

---

## Herramientas Recomendadas para Ejecución

### Automatización
```bash
# Instalar dependencias de testing
pip install pytest pytest-asyncio httpx pytest-cov

# Ejecutar todas las pruebas
pytest -v --cov=app --cov-report=html

# Ejecutar pruebas específicas
pytest tests/test_auth.py -v
pytest tests/test_admin_api.py -k "test_create_supplier"
```

### Monitoreo y Debugging
```bash
# Ver logs en tiempo real
tail -f logs/app.log | jq '.'  # Si logs son JSON

# Verificar base de datos
sqlite3 test.db ".tables"
sqlite3 test.db "SELECT * FROM users LIMIT 5;"

# Probar endpoints manualmente
http POST localhost:8000/api/v1/auth/login email=admin@comercializadora.com password=Admin123!
```

---

## Notas de Implementación para Pruebas

### Configuración de Entorno de Testing
```python
# En settings.py
ENVIRONMENT = "testing"
DATABASE_URL = "sqlite:///./test.db"
SECRET_KEY = "test-secret-key-change-in-production"
```

### Fixtures de Prueba Recomendadas
- Usuario administrador con token válido
- Suppliers de prueba (activos/inactivos)
- Storefronts con diferentes configuraciones
- API Keys válidas e inválidas

### Consideraciones Especiales
1. **Reset de base de datos** entre suites de pruebas
2. **Mock de servicios externos** (email, SMS, APIs de pago)
3. **Pruebas de concurrencia** para operaciones concurrentes
4. **Pruebas de migración** al actualizar esquemas de DB

---

## Checklist de Preparación para Producción

- [ ] Variables de entorno configuradas (producción)
- [ ] SECRET_KEY generada aleatoriamente
- [ ] CORS configurado para dominios permitidos
- [ ] Rate limiting habilitado
- [ ] Logs configurados para aggregación
- [ ] Health checks implementados
- [ ] Backup de base de datos configurado
- [ ] Monitoreo y alertas configurados
- [ ] Documentación de API actualizada
- [ ] Plan de rollback definido