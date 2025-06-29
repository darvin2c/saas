from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from uuid import UUID
from app.database import get_db
from app.services.auth_service import AuthService
from app.services.user_service import UserService
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


def verify_user_in_tenant(tenant_id: UUID):
    """Verify that the current user belongs to the specified tenant."""
    def tenant_checker(current_user: TokenData = Depends(get_current_user), db: Session = Depends(get_db)):
        if not UserService.check_user_in_tenant(db, current_user.user_id, tenant_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not belong to this tenant"
            )
        return current_user
    return tenant_checker
