from pydantic import BaseSettings
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()


class Settings(BaseSettings):
    """
    Configuración de la aplicación utilizando Pydantic BaseSettings.
    Las variables de entorno tienen prioridad sobre los valores predeterminados.
    """
    # Configuración general de la aplicación
    APP_NAME: str = "API Gateway Service"
    GATEWAY_HOST: str = os.getenv("GATEWAY_HOST", "0.0.0.0")
    GATEWAY_PORT: int = int(os.getenv("GATEWAY_PORT", "8000"))
    
    # Configuración de CORS
    CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    
    # Configuración de JWT
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    
    # Configuración de servicios
    # Diccionario con la configuración de cada servicio
    SERVICES: Dict[str, Dict[str, Any]] = {
        "auth": {
            "url": os.getenv("AUTH_SERVICE_URL", "http://localhost:8001"),
            "public_paths": [
                "login",
                "register",
                "reset-password",
                "verify-email",
                "health"
            ],
            "permissions": {
                "users": ["admin"],
                "roles": ["admin"]
            }
        },
        "dentist": {
            "url": os.getenv("DENTIST_SERVICE_URL", "http://localhost:8002"),
            "public_paths": [
                "health"
            ],
            "permissions": {
                "patients": ["dentist", "admin"],
                "appointments": ["dentist", "admin"],
                "treatments": ["dentist", "admin"]
            }
        }
    }


# Instancia de configuración para uso en toda la aplicación
settings = Settings()
