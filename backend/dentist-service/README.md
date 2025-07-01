# Dentist Service

Servicio de gestión para clínicas dentales con funcionalidades para administrar pacientes, citas y tratamientos.

## Descripción

El Dentist Service es un microservicio que forma parte de una arquitectura SaaS multi-tenant. Este servicio se encarga de gestionar toda la información relacionada con pacientes dentales y está diseñado para trabajar en conjunto con el servicio de autenticación.

## Características

- **Gestión de pacientes**: Crear, leer, actualizar y eliminar información de pacientes
- **Arquitectura multi-tenant**: Cada clínica dental (tenant) tiene acceso únicamente a sus propios datos
- **API RESTful**: Interfaz clara y consistente para interactuar con el servicio
- **Integración con Auth Service**: Validación de tokens y permisos

## Estructura del proyecto

```
dentist-service/
├── app/
│   ├── api/             # Endpoints de la API
│   ├── models/          # Modelos de datos (SQLAlchemy)
│   ├── schemas/         # Esquemas de validación (Pydantic)
│   ├── services/        # Lógica de negocio
│   ├── utils/           # Utilidades y helpers
│   ├── config.py        # Configuración del servicio
│   ├── database.py      # Configuración de la base de datos
│   └── main.py          # Punto de entrada de la aplicación
├── tests/               # Tests unitarios y de integración
├── requirements.txt     # Dependencias del proyecto
├── run_tests.ps1        # Script para ejecutar tests en Windows
└── run_tests.sh         # Script para ejecutar tests en Linux
```

## Requisitos

- Python 3.9+
- PostgreSQL 13+
- Servicio de autenticación configurado y en ejecución

## Instalación

1. Clonar el repositorio
2. Crear un entorno virtual:
   ```
   python -m venv .venv
   ```
3. Activar el entorno virtual:
   - Windows: `.venv\Scripts\activate`
   - Linux/Mac: `source .venv/bin/activate`
4. Instalar dependencias:
   ```
   pip install -r requirements.txt
   ```
5. Configurar variables de entorno (o crear archivo `.env`):
   ```
   DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/dentist_service
   SECRET_KEY=tu_clave_secreta
   AUTH_SERVICE_URL=http://localhost:8000
   ```

## Uso

### Iniciar el servicio

```
cd dentist-service
python -m app.main
```

El servicio estará disponible en `http://localhost:8001`

### Endpoints principales

- `GET /{tenant_id}/patients` - Listar todos los pacientes
- `GET /{tenant_id}/patients/search` - Buscar pacientes
- `GET /{tenant_id}/patients/{patient_id}` - Obtener un paciente específico
- `POST /{tenant_id}/patients` - Crear un nuevo paciente
- `PUT /{tenant_id}/patients/{patient_id}` - Actualizar un paciente
- `DELETE /{tenant_id}/patients/{patient_id}` - Eliminar un paciente

## Ejecutar pruebas

### Windows

```
.\run_tests.ps1
```

Para ejecutar con cobertura:

```
.\run_tests.ps1 -Coverage
```

### Linux

```
chmod +x run_tests.sh
./run_tests.sh
```

Para ejecutar con cobertura:

```
./run_tests.sh --coverage
```

## Integración con otros servicios

Este servicio está diseñado para trabajar con:

- **Auth Service**: Para autenticación y validación de tokens
- **Gateway Service**: Como punto de entrada para todas las solicitudes API

## Esquema de base de datos

El servicio utiliza un esquema dedicado llamado `dentist` en la base de datos PostgreSQL para almacenar todas sus tablas, manteniendo una clara separación de los datos de otros servicios.

## Licencia

Este proyecto está licenciado bajo los términos de la licencia MIT.
