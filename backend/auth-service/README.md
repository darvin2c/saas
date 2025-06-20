# Auth Service - Microservicio de Autenticación para SaaS

Este repositorio contiene el servicio de autenticación para una arquitectura de microservicios SaaS. Como parte de una infraestructura modular, este servicio está diseñado para funcionar de manera independiente y comunicarse con otros servicios a través de un API Gateway. El servicio implementa autenticación multi-tenant con roles dinámicos y permisos granulares, proporcionando una base sólida para aplicaciones SaaS escalables.

## Características

- **Arquitectura Multi-tenant**: Soporte completo para múltiples inquilinos (tenants) con aislamiento de datos
- **Autenticación JWT**: Implementación segura con tokens de acceso y refresco
- **Roles y Permisos**: Sistema de roles dinámicos con permisos granulares
- **Verificación de Email**: Proceso de verificación de cuentas por email
- **Recuperación de Contraseña**: Flujo seguro para restablecer contraseñas
- **API RESTful**: Endpoints bien documentados siguiendo principios REST
- **Tests Automatizados**: Cobertura de pruebas para garantizar la calidad del código

## Tecnologías

- **FastAPI**: Framework web de alto rendimiento para APIs con tipado estático
- **SQLAlchemy**: ORM para interacción con la base de datos
- **PostgreSQL**: Base de datos relacional con soporte para esquemas y multi-tenancy
- **Pydantic**: Validación de datos, serialización y configuración
- **Alembic**: Migraciones de base de datos
- **Pytest**: Framework de pruebas con soporte para pruebas asíncronas
- **JWT**: Autenticación basada en tokens con soporte para claims personalizados
- **Passlib**: Manejo seguro de contraseñas con algoritmos modernos
- **Docker**: Contenerización para despliegue consistente (opcional)

## Estructura del Proyecto

```
auth-service/
├── alembic/                # Migraciones de base de datos
├── app/
│   ├── api/                # Endpoints de la API
│   │   ├── auth.py         # Endpoints de autenticación
│   │   ├── users.py        # Gestión de usuarios
│   │   ├── tenants.py      # Gestión de inquilinos
│   │   ├── roles.py        # Gestión de roles
│   │   └── permissions.py  # Gestión de permisos
│   ├── models/             # Modelos de SQLAlchemy
│   │   ├── user.py
│   │   ├── tenant.py
│   │   ├── role.py
│   │   ├── permission.py
│   │   └── user_tenant_role.py
│   ├── schemas/            # Esquemas de Pydantic
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── tenant.py
│   │   ├── role.py
│   │   └── permission.py
│   ├── services/           # Lógica de negocio
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── tenant_service.py
│   │   ├── role_service.py
│   │   └── permission_service.py
│   ├── utils/              # Utilidades
│   ├── config.py           # Configuración de la aplicación
│   ├── database.py         # Configuración de la base de datos
│   └── main.py             # Punto de entrada de la aplicación
├── tests/                  # Pruebas automatizadas
│   ├── conftest.py         # Configuración de pruebas
│   └── services/           # Pruebas de servicios
├── .env                    # Variables de entorno (no incluido en el repositorio)
├── .env.test               # Variables de entorno para pruebas
├── alembic.ini             # Configuración de Alembic
└── requirements.txt        # Dependencias del proyecto
```

## Modelos de Datos

### User (Usuario)
- Información básica del usuario (email, nombre, contraseña)
- Estado de verificación
- Fecha de último acceso

### Tenant (Inquilino)
- Información del inquilino (nombre, dominio)
- Estado de activación

### Role (Rol)
- Roles configurables por inquilino
- Descripción y nivel de acceso

### Permission (Permiso)
- Permisos granulares para acciones específicas
- Formato: `acción:ámbito` (ej. `read:users`, `write:own`)

### UserTenantRole
- Relación entre usuarios, inquilinos y roles
- Un usuario puede pertenecer a múltiples inquilinos con diferentes roles

## Configuración

1. Crea un archivo `.env` en la raíz del proyecto con las siguientes variables (reemplaza los valores con tus configuraciones):

```
DATABASE_URL=postgresql://****:****@localhost:5432/auth_db
SECRET_KEY=**********************
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_USERNAME=****@example.com
EMAIL_PASSWORD=************
APP_NAME=Auth Service
DEBUG=False
```

> **IMPORTANTE**: Nunca compartas tu archivo `.env` ni lo subas al repositorio. Asegúrate de incluirlo en `.gitignore`.

2. Crea la base de datos y el esquema:

```sql
CREATE DATABASE auth_db;
CREATE SCHEMA auth;
```

3. Ejecuta las migraciones:

```bash
alembic upgrade head
```

## Ejecución

Para ejecutar el servicio en modo desarrollo:

```bash
uvicorn app.main:app --reload
```

## Pruebas

El servicio incluye pruebas unitarias e integración para garantizar su correcto funcionamiento.

### Configuración de pruebas

1. Asegúrate de tener un archivo `.env.test` con la configuración para el entorno de pruebas
2. Las pruebas utilizan una base de datos separada que se crea y destruye durante la ejecución

### Ejecución de pruebas

```bash
# Ejecutar todas las pruebas
pytest

# Ejecutar pruebas específicas
pytest tests/services/test_auth_service.py

# Ejecutar con cobertura
pytest --cov=app

# Ejecutar pruebas fallidas anteriormente
pytest --lf

# Ejecutar pruebas con salida detallada
pytest -v
```

### Mocks y fixtures

El proyecto utiliza fixtures de pytest para configurar el entorno de pruebas y mocks para simular servicios externos como el envío de emails.

## Endpoints Principales

### Autenticación
- `POST /auth/register`: Registro de usuario
- `POST /auth/login`: Inicio de sesión
- `POST /auth/refresh`: Renovar token de acceso
- `POST /auth/verify-email`: Verificar email
- `POST /auth/request-password-reset`: Solicitar restablecimiento de contraseña
- `POST /auth/reset-password`: Restablecer contraseña

### Usuarios
- `GET /users/me`: Obtener información del usuario actual
- `PUT /users/me`: Actualizar información del usuario actual
- `GET /users`: Listar usuarios (admin)
- `GET /users/{user_id}`: Obtener usuario específico (admin)

### Inquilinos (Tenants)
- `GET /tenants`: Listar inquilinos
- `POST /tenants`: Crear nuevo inquilino
- `GET /tenants/{tenant_id}`: Obtener inquilino específico
- `PUT /tenants/{tenant_id}`: Actualizar inquilino
- `DELETE /tenants/{tenant_id}`: Eliminar inquilino

### Roles
- `GET /roles`: Listar roles
- `POST /roles`: Crear nuevo rol
- `GET /roles/{role_id}`: Obtener rol específico
- `PUT /roles/{role_id}`: Actualizar rol
- `DELETE /roles/{role_id}`: Eliminar rol
- `POST /roles/{role_id}/permissions`: Asignar permisos a rol

### Permisos
- `GET /permissions`: Listar permisos
- `POST /permissions`: Crear nuevo permiso
- `GET /permissions/{permission_id}`: Obtener permiso específico
- `PUT /permissions/{permission_id}`: Actualizar permiso
- `DELETE /permissions/{permission_id}`: Eliminar permiso

## Arquitectura e Integración con otros Microservicios

Este servicio de autenticación es parte de una arquitectura de microservicios SaaS completa, diseñado para integrarse con otros servicios a través de un API Gateway.

### Diagrama de Arquitectura

```
+-------------+     +----------------+     +-----------------+
|             |     |                |     |                 |
|  Cliente    +---->+  API Gateway   +---->+ Auth Service    |
|  (Frontend) |     |                |     | (Este servicio) |
|             |     |                |     |                 |
+------+------+     +--------+-------+     +-----------------+
       |                     |
       |                     |     +-----------------+
       |                     +---->+                 |
       |                           | Otros Servicios |
       +-------------------------->+ (Recursos SaaS) |
                                   |                 |
                                   +-----------------+
```

### Principios de la Arquitectura

- **API Gateway**: Punto de entrada único que enruta las solicitudes a los servicios apropiados
- **Comunicación entre Servicios**: Mediante HTTP/REST o mensajería asíncrona
- **Autenticación Centralizada**: Este servicio proporciona tokens JWT que pueden ser validados por otros microservicios
- **Autorización Distribuida**: Los permisos definidos aquí pueden ser utilizados por otros servicios para control de acceso
- **Aislamiento de Datos**: Cada inquilino (tenant) tiene sus datos aislados lógicamente

### Flujo de Autenticación

1. El usuario se autentica contra este servicio
2. Recibe un token JWT con información de identidad, tenant y permisos
3. El token se envía en las solicitudes a otros servicios a través del API Gateway
4. Cada microservicio valida el token y autoriza las operaciones según los permisos

### Escalabilidad

La arquitectura está diseñada para escalar horizontalmente:

- Cada microservicio puede escalarse de forma independiente según sus necesidades
- El esquema multi-tenant permite optimizar recursos compartiendo infraestructura
- La separación de responsabilidades facilita el mantenimiento y la evolución del sistema

## Consideraciones de Seguridad

- Los tokens JWT están firmados con una clave secreta
- Las contraseñas se almacenan con hash seguro
- Se implementa protección contra ataques comunes (CSRF, XSS)
- Se utilizan cabeceras de seguridad recomendadas
- Comunicación segura entre microservicios

## Contribución

1. Haz un fork del repositorio
2. Crea una rama para tu característica (`git checkout -b feature/amazing-feature`)
3. Haz commit de tus cambios (`git commit -m 'Add some amazing feature'`)
4. Haz push a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

## Licencia

Este proyecto está licenciado bajo [MIT License](LICENSE).
