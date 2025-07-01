from fastapi import Depends, HTTPException, status, Path
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError
from typing import Optional
from uuid import UUID
import httpx

from app.config import settings

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def validate_token(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Validate the access token and return the user data.
    This function will call the auth service to validate the token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Call the auth service to validate the token
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.AUTH_SERVICE_URL}/auth/validate-token",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code != 200:
                raise credentials_exception
            
            return response.json()
            
    except (JWTError, ValidationError, httpx.RequestError):
        raise credentials_exception


def get_tenant_id_from_path(tenant_id: UUID = Path(..., description="ID del tenant")) -> UUID:
    """
    Get the tenant_id from the URL path.
    """
    return tenant_id
