from fastapi import APIRouter, Request, HTTPException, status
from app.config.settings import settings
from app.utils.proxy import forward_request_to_service
from app.utils.auth import verify_token
import logging

# Configurar logging
logger = logging.getLogger("gateway-service")

# Crear un router para todos los servicios
router = APIRouter()


def is_public_path(path: str, public_paths: list) -> bool:
    """
    Verifica si una ruta es pública comparando con los prefijos de rutas públicas.
    
    Args:
        path: La ruta a verificar
        public_paths: Lista de prefijos de rutas públicas
        
    Returns:
        True si la ruta es pública, False en caso contrario
    """
    # Primero verificar coincidencia exacta
    if path in public_paths:
        return True
    
    # Luego verificar si la ruta comienza con alguno de los prefijos públicos
    for public_path in public_paths:
        if path.startswith(public_path + '/'):
            return True
    
    return False


@router.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def service_proxy(service: str, path: str, request: Request):
    """
    Proxy dinámico para todos los servicios configurados.
    
    Args:
        service: El nombre del servicio (auth, dentist, etc.)
        path: La ruta a reenviar al servicio
        request: La solicitud entrante
    
    Returns:
        La respuesta del servicio
    """
    # Verificar si el servicio está configurado
    if service not in settings.SERVICES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Servicio '{service}' no encontrado"
        )
    
    # Obtener la configuración del servicio
    service_config = settings.SERVICES[service]
    service_url = service_config["url"]
    public_paths = service_config["public_paths"]
    
    # Verificar si la ruta requiere autenticación usando la función mejorada
    if not is_public_path(path, public_paths):
        try:
            # Solo verificar el token para rutas protegidas
            # La autorización será responsabilidad de cada servicio
            await verify_token(request)
            logger.info(f"Token verificado para la ruta {path}")
        except HTTPException as e:
            raise e
    else:
        logger.info(f"Ruta pública: {path}")
    
    # Reenviar la solicitud al servicio correspondiente
    return await forward_request_to_service(request, service_url)
