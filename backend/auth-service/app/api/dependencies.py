from typing import Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.auth_service import AuthService
from app.schemas.auth import TokenData

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> TokenData:
    """Get current authenticated user from JWT token."""
    token = credentials.credentials
    token_data = AuthService.verify_access_token(db, token)
    
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return token_data


def require_permissions(required_permissions: List[str]):
    """Dependency to check if user has required permissions."""
    def permission_checker(current_user: TokenData = Depends(get_current_user)):
        user_permissions = set(current_user.permissions)
        required_permissions_set = set(required_permissions)
        
        if not required_permissions_set.issubset(user_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        return current_user
    
    return permission_checker


def require_any_permission(required_permissions: List[str]):
    """Dependency to check if user has any of the required permissions."""
    def permission_checker(current_user: TokenData = Depends(get_current_user)):
        user_permissions = set(current_user.permissions)
        required_permissions_set = set(required_permissions)
        
        if not user_permissions.intersection(required_permissions_set):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        return current_user
    
    return permission_checker


# Common permission dependencies
require_user_read = require_permissions(["users:read"])
require_user_create = require_permissions(["users:create"])
require_user_update = require_permissions(["users:update"])
require_user_delete = require_permissions(["users:delete"])

require_role_read = require_permissions(["roles:read"])
require_role_create = require_permissions(["roles:create"])
require_role_update = require_permissions(["roles:update"])
require_role_delete = require_permissions(["roles:delete"])

require_tenant_read = require_permissions(["tenant:read"])
require_tenant_update = require_permissions(["tenant:update"])
