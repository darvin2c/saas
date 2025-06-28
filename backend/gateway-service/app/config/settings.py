from typing import List, Dict, Any
import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configuración de la aplicación utilizando pydantic-settings.
    Las variables de entorno tienen prioridad sobre los valores predeterminados.
    """
    # Configuración del modelo
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')
    
    # Configuración general de la aplicación
    APP_NAME: str = "API Gateway Service"
    
    # Configuración de CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Configuración de JWT
    JWT_SECRET_KEY: str = "your-secret-key"
    JWT_ALGORITHM: str = "HS256"
    
    # Configuración de servicios
    # Diccionario con la configuración de cada servicio
    AUTH_SERVICE_URL: str = "http://localhost:8001"
    DENTIST_SERVICE_URL: str = "http://localhost:8002"
    
    @property
    def SERVICES(self) -> Dict[str, Dict[str, Any]]:
        return {
            "auth": {
                "url": self.AUTH_SERVICE_URL,
                "public_paths": [
                    "login",
                    "register",
                    "reset-password",
                    "verify-email",
                    "health"
                ]
            },
            "dentist": {
                "url": self.DENTIST_SERVICE_URL,
                "public_paths": [
                    "health"
                ]
            }
        }


# Instancia de configuración para uso en toda la aplicación
settings = Settings()
