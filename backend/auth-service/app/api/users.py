from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import User, UserCreate, UserUpdate, UserWithTenant
from app.schemas.auth import TokenData
from app.services.user_service import UserService
from app.services.user_tenant_service import UserTenantService
from app.api.dependencies import get_current_user
import app.models

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/exists", response_model=dict)
async def check_email(email: str = Query(..., description="Email to check"), db: Session = Depends(get_db)):
    """Check if email exists."""
    user = UserService.get_user_by_email(db, email)
    return {"exists": user is not None}


@router.get("/me", response_model=User)
def get_current_user_info(
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user information."""
    user = UserService.get_user(db, current_user.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.patch("/me", response_model=User)
def update_current_user(
    user_update: UserUpdate,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user information."""
    user = UserService.update_user(db, current_user.user_id, user_update)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user



@router.get("/", response_model=List[User])
def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=100),
    tenant_id: UUID = Query(..., description="Tenant ID to filter users"),
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all users in the current tenant."""
    # Check if user belongs to the tenant
    if not UserService.check_user_in_tenant(db, current_user.user_id, tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not belong to this tenant"
        )
    
    users = UserService.get_tenant_users(db, tenant_id, skip, limit)
    return users


@router.get("/{user_id}", response_model=User)
def get_user(
    user_id: UUID,
    tenant_id: UUID = Query(..., description="Tenant ID"),
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user by ID."""
    # Check if current user belongs to the tenant
    if not UserService.check_user_in_tenant(db, current_user.user_id, tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not belong to this tenant"
        )
    
    user = UserService.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if requested user belongs to the tenant
    if not UserService.check_user_in_tenant(db, user_id, tenant_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in this tenant"
        )
    
    return user


@router.post("/", response_model=User)
async def create_user(
    user: UserCreate,
    tenant_id: UUID = Query(..., description="Tenant ID"),
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new user in the specified tenant."""
    # Check if current user belongs to the tenant
    if not UserService.check_user_in_tenant(db, current_user.user_id, tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not belong to this tenant"
        )
    
    # Check if user already exists
    existing_user = UserService.get_user_by_email(db, user.email)
    if existing_user:
        # Check if user already belongs to this tenant
        if UserService.check_user_in_tenant(db, existing_user.id, tenant_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists in this tenant"
            )
    
    # Create new user
    new_user = UserService.create_user(db, user, tenant_id)
    
    # Create user-tenant relationship
    from app.schemas.user_tenant import UserTenantCreate
    user_tenant_data = UserTenantCreate(
        user_id=new_user.id,
        tenant_id=tenant_id
    )
    UserTenantService.create_user_tenant(db, user_tenant_data)
    
    return new_user


@router.patch("/{user_id}", response_model=User)
def update_user(
    user_id: UUID,
    user_update: UserUpdate,
    tenant_id: UUID = Query(..., description="Tenant ID"),
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user partially."""
    # Check if current user belongs to the tenant
    if not UserService.check_user_in_tenant(db, current_user.user_id, tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not belong to this tenant"
        )
    
    # Check if user to update belongs to the tenant
    if not UserService.check_user_in_tenant(db, user_id, tenant_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in this tenant"
        )
    
    updated_user = UserService.update_user(db, user_id, user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return updated_user


@router.delete("/{user_id}")
def delete_user(
    user_id: UUID,
    tenant_id: UUID = Query(..., description="Tenant ID"),
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete user from a tenant."""
    # Check if current user belongs to the tenant
    if not UserService.check_user_in_tenant(db, current_user.user_id, tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not belong to this tenant"
        )
    
    # Check if user to delete belongs to the tenant
    if not UserService.check_user_in_tenant(db, user_id, tenant_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in this tenant"
        )
    
    # Cannot delete yourself
    if user_id == current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself"
        )
    
    # Delete user-tenant relationship instead of the user
    user_tenant = db.query(app.models.UserTenant).filter(
        app.models.UserTenant.user_id == user_id,
        app.models.UserTenant.tenant_id == tenant_id
    ).first()
    
    if not user_tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in this tenant"
        )
    
    db.delete(user_tenant)
    db.commit()
    
    return {"message": "User removed from tenant successfully"}
