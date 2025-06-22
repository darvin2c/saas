# Backend SaaS Multi-Tenant con FastAPI y SQLModel

Backend para aplicación SaaS con:

- Arquitectura de microservicios
- Autenticación JWT
- Base de datos PostgreSQL
- API RESTful con FastAPI
- Testing automatizado con GitHub Actions

## Estructura de Microservicios

El backend está organizado en varios microservicios independientes:

- **auth-service**: Gestión de autenticación y autorización
- **gateway-service**: API Gateway y enrutamiento
- **dentist-service**: Servicios específicos para dentistas (en desarrollo)

## Requisitos

- Python 3.8+
- PostgreSQL
- PowerShell (para Windows)

## Configuración del Entorno

Cada microservicio tiene su propio entorno virtual y dependencias. Los scripts centralizados se encargan de gestionar estos entornos automáticamente.

### Variables de Entorno

Configura las siguientes variables en cada servicio:

```
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/saas_db
```

Para tests, se usa automáticamente la base de datos `saas_test`.

## Scripts de Desarrollo y Testing

### Desarrollo

Para iniciar todos los servicios:

```powershell
.\dev.ps1 --start
```

Para iniciar un servicio específico:

```powershell
.\dev.ps1 --start auth-service
```

Para detener los servicios:

```powershell
.\dev.ps1 --stop
```

### Testing

Para ejecutar todos los tests:

```powershell
.\tests.ps1
```

Para ejecutar tests de un servicio específico:

```powershell
.\tests.ps1 auth-service
```

Para ejecutar un archivo de test específico:

```powershell
.\tests.ps1 auth-service --test-file test_auth.py
```

## Estructura del Proyecto

```
backend/
├── .github/workflows/    # Configuración de GitHub Actions
├── auth-service/         # Servicio de autenticación
│   ├── alembic/          # Migraciones de base de datos
│   ├── app/              # Código principal
│   ├── tests/            # Tests del servicio
│   ├── requirements.txt  # Dependencias
│   └── run_tests.ps1     # Script de tests específico
├── gateway-service/      # Servicio de API Gateway
│   ├── app/              # Código principal
│   ├── tests/            # Tests del servicio
│   ├── requirements.txt  # Dependencias
│   └── run_tests.ps1     # Script de tests específico
├── dentist-service/      # Servicio para dentistas (en desarrollo)
├── dev.ps1               # Script para desarrollo
├── tests.ps1             # Script para tests
├── setup_test_db.py      # Configuración de base de datos para tests
└── README.md             # Este archivo
```

## Integración Continua

El proyecto utiliza GitHub Actions para la integración continua. El workflow ejecuta automáticamente:

1. Configuración del entorno PostgreSQL
2. Creación de la base de datos de tests
3. Configuración de entornos virtuales para cada servicio
4. Ejecución de tests para todos los servicios

El workflow se activa con push/pull requests a las ramas principales o manualmente desde GitHub.
