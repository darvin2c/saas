# API Gateway Service

Este servicio actúa como punto de entrada centralizado para todos los microservicios en la arquitectura SaaS. Proporciona enrutamiento dinámico, autenticación y autorización para las solicitudes a los diferentes servicios.

## Características

- **Enrutamiento dinámico**: Reenvía solicitudes a los microservicios correspondientes basado en la configuración.
- **Autenticación centralizada**: Verifica tokens JWT para rutas protegidas.
- **Autorización por permisos**: Verifica que los usuarios tengan los permisos necesarios para acceder a ciertas rutas.
- **Configuración dinámica de servicios**: Permite agregar nuevos servicios sin modificar el código.
- **Logging**: Registro detallado de solicitudes y respuestas.
- **Manejo de errores**: Respuestas de error consistentes y manejo de excepciones.

## Estructura del proyecto

```
gateway-service/
├── .venv/                  # Entorno virtual de Python
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   └── router.py       # Router dinámico para todos los servicios
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py     # Configuración de la aplicación
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── auth.py         # Utilidades de autenticación
│   │   └── proxy.py        # Utilidades para reenviar solicitudes
│   ├── __init__.py
│   └── main.py             # Punto de entrada de la aplicación
├── .env.example            # Ejemplo de variables de entorno
└── README.md               # Este archivo
```

## Configuración

La configuración se maneja a través de variables de entorno. Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```
# Configuración del gateway
CORS_ORIGINS=http://localhost:3000,https://example.com

# Configuración de JWT
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256

# URLs de servicios
AUTH_SERVICE_URL=http://localhost:8001
DENTIST_SERVICE_URL=http://localhost:8002
```

## Servicios configurados

Los servicios se configuran en `app/config/settings.py`. Cada servicio tiene:

- **URL**: La URL base del servicio.
- **Rutas públicas**: Lista de rutas que no requieren autenticación.
- **Permisos**: Mapeo de prefijos de ruta a permisos requeridos.

## Ejecución

1. Activa el entorno virtual:
   ```
   .\.venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/Mac
   ```

2. Ejecuta la aplicación:
   ```
   uvicorn app.main:app --reload
   ```

3. Accede a la documentación en `http://localhost:8000/docs`

## Agregar un nuevo servicio

Para agregar un nuevo servicio, actualiza el diccionario `SERVICES` en `app/config/settings.py`:

```python
"nuevo_servicio": {
    "url": os.getenv("NUEVO_SERVICIO_URL", "http://localhost:8003"),
    "public_paths": [
        "health",
        "otra-ruta-publica"
    ],
    "permissions": {
        "ruta-protegida": ["permiso1", "permiso2"]
    }
}
```

No es necesario modificar ningún otro código, ya que el enrutador dinámico manejará automáticamente el nuevo servicio.
