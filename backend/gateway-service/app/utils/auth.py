from fastapi import Request, HTTPException, status
from jose import jwt, JWTError
from app.config.settings import settings
from typing import Dict, Any
import logging

# Configurar logging
logger = logging.getLogger("gateway-service")


async def verify_token(request: Request) -> Dict[str, Any]:
    """
    Verifica el token JWT en el encabezado de la solicitud.
    
    Args:
        request: La solicitud entrante con el encabezado Authorization
        
    Returns:
        El payload del token decodificado
        
    Raises:
        HTTPException: Si el token es inválido o falta
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        logger.warning(f"Solicitud sin encabezado de autorización: {request.url.path}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Encabezado de autorización faltante",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Extraer token del encabezado (Bearer token)
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            logger.warning(f"Esquema de autenticación inválido: {auth_header}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Esquema de autenticación inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token = parts[1]
        
        # Decodificar y verificar el token
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        # Registrar información útil para depuración
        logger.debug(f"Token válido para usuario: {payload.get('sub', 'desconocido')}")
        
        return payload
    except JWTError as e:
        logger.warning(f"Error de token JWT: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Error inesperado al verificar token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error de autenticación",
            headers={"WWW-Authenticate": "Bearer"},
        )
