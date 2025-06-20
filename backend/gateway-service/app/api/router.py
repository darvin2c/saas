from fastapi import APIRouter, Request, HTTPException, status
from app.config.settings import settings
from app.utils.proxy import forward_request_to_service
from app.utils.auth import verify_token, check_permissions
import logging

# Configurar logging
logger = logging.getLogger("gateway-service")

# Crear un router para todos los servicios
router = APIRouter()


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
    permissions = service_config["permissions"]
    
    # Verificar si la ruta requiere autenticación
    if path not in public_paths:
        try:
            # Verificar el token para rutas protegidas
            token_payload = await verify_token(request)
            
            # Verificar permisos específicos para ciertas rutas
            for route_prefix, required_permissions in permissions.items():
                if path.startswith(route_prefix):
                    has_permission = await check_permissions(request, required_permissions)
                    if not has_permission:
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail="Permisos insuficientes"
                        )
        except HTTPException as e:
            raise e
    
    # Reenviar la solicitud al servicio correspondiente
    return await forward_request_to_service(request, service_url)
