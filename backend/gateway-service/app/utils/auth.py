from fastapi import Request, HTTPException, status
from jose import jwt, JWTError
from app.config.settings import settings
from typing import Dict, Any, Optional, List
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


async def check_permissions(request: Request, required_permissions: Optional[List[str]] = None) -> bool:
    """
    Verifica si el usuario tiene los permisos requeridos.
    
    Args:
        request: La solicitud entrante
        required_permissions: Lista de permisos requeridos
        
    Returns:
        True si el usuario tiene los permisos requeridos, False en caso contrario
    """
    if not required_permissions:
        return True
    
    try:
        # Obtener el payload del token
        payload = await verify_token(request)
        
        # Extraer permisos del token
        user_permissions = payload.get("permissions", [])
        tenant_id = payload.get("tenant_id")
        user_id = payload.get("user_id")
        
        # Registrar información para depuración
        logger.debug(
            f"Verificando permisos para usuario {user_id} en tenant {tenant_id}. "
            f"Permisos requeridos: {required_permissions}, "
            f"Permisos del usuario: {user_permissions}"
        )
        
        # Verificar si el usuario tiene todos los permisos requeridos
        has_permissions = all(perm in user_permissions for perm in required_permissions)
        
        if not has_permissions:
            logger.warning(
                f"Acceso denegado para usuario {user_id} en tenant {tenant_id}. "
                f"Faltan permisos: {[p for p in required_permissions if p not in user_permissions]}"
            )
        
        return has_permissions
    except HTTPException as e:
        logger.warning(f"Error de autenticación al verificar permisos: {e.detail}")
        return False
    except Exception as e:
        logger.error(f"Error inesperado al verificar permisos: {str(e)}")
        return False
