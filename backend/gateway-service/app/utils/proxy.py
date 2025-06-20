import httpx
from fastapi import Request, Response
import logging

# Configurar logging
logger = logging.getLogger("gateway-service")


async def forward_request_to_service(request: Request, service_url: str) -> Response:
    """
    Reenvía una solicitud a un servicio específico y devuelve la respuesta.
    
    Args:
        request: La solicitud entrante
        service_url: La URL base del servicio
    
    Returns:
        La respuesta del servicio
    """
    # Extraer la ruta de la URL
    path = request.url.path
    
    # Obtener el nombre del servicio de la ruta (primer segmento después de /)
    service_name = path.split('/')[1] if len(path.split('/')) > 1 else ''
    
    # Eliminar el prefijo del servicio de la ruta (ej: /auth/users -> /users)
    path_without_service = '/' + '/'.join(path.split('/')[2:]) if len(path.split('/')) > 2 else '/'
    
    # Construir la URL de destino
    target_path = f"{service_url}{path_without_service}"
    if request.url.query:
        target_path = f"{target_path}?{request.url.query}"
    
    logger.debug(f"Reenviando solicitud a {service_name}: {path} -> {target_path}")
    
    # Obtener el cuerpo de la solicitud
    body = await request.body()
    
    # Obtener los encabezados de la solicitud
    headers = dict(request.headers)
    # Eliminar encabezados que podrían causar problemas
    headers.pop("host", None)
    
    try:
        # Crear un cliente httpx para la solicitud
        async with httpx.AsyncClient() as client:
            # Reenviar la solicitud al servicio de destino
            response = await client.request(
                method=request.method,
                url=target_path,
                headers=headers,
                content=body,
                cookies=request.cookies,
                follow_redirects=True,
                timeout=30.0  # Tiempo de espera de 30 segundos
            )
            
            # Crear una respuesta con el contenido del servicio de destino
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.headers.get("content-type")
            )
    except httpx.RequestError as e:
        logger.error(f"Error al conectar con el servicio {service_name}: {str(e)}")
        return Response(
            content=f"{{\"detail\": \"Error al conectar con el servicio {service_name}: {str(e)}\"}}".encode(),
            status_code=503,  # Service Unavailable
            media_type="application/json"
        )
    except Exception as e:
        logger.error(f"Error inesperado al procesar la solicitud: {str(e)}")
        return Response(
            content="{\"detail\": \"Error interno del servidor\"}".encode(),
            status_code=500,  # Internal Server Error
            media_type="application/json"
        )
