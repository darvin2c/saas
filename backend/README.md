# Backend SaaS Multi-Tenant con FastAPI y SQLModel

Este proyecto implementa un backend para aplicaciones SaaS con capacidades multi-tenant, utilizando FastAPI como framework web y SQLModel para la gestión de modelos y base de datos.

## Características

- Arquitectura multi-tenant
- Sistema completo de autenticación y autorización
- Modelos de datos con SQLModel
- Migraciones de base de datos con Alembic
- API RESTful con FastAPI

## Requisitos

- Python 3.8+
- PostgreSQL

## Instalación

1. Clonar el repositorio
2. Crear un entorno virtual: `python -m venv venv`
3. Activar el entorno virtual:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Instalar dependencias: `pip install -r requirements.txt`
5. Configurar variables de entorno en `.env`
6. Ejecutar migraciones: `alembic upgrade head`
7. Iniciar el servidor: `uvicorn app.main:app --reload`

## Estructura del Proyecto

```
.
├── alembic/              # Configuración y migraciones de Alembic
├── app/                  # Código principal
│   ├── api/              # Endpoints de la API
│   ├── auth/             # Autenticación y autorización
│   ├── core/             # Configuración central
│   ├── db/               # Configuración de la base de datos
│   ├── models/           # Modelos de datos SQLModel
│   ├── schemas/          # Esquemas Pydantic
│   └── services/         # Lógica de negocio
├── tests/                # Pruebas
└── .env                  # Variables de entorno (no incluido en repo)
```
