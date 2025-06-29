from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import User, UserCreate, UserUpdate, UserWithTenantRole
from app.schemas.auth import TokenData
from app.services.user_service import UserService
from app.services.role_service import RoleService
from app.api.dependencies import (
    get_current_user, require_user_read, require_user_create, 
    require_user_update, require_user_delete
)

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


@router.get("/", response_model=List[User])
def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=100),
    current_user: TokenData = Depends(require_user_read),
    db: Session = Depends(get_db)
):
    """Get all users in the current tenant."""
    users = UserService.get_tenant_users(db, current_user.tenant_id, skip, limit)
    return users


@router.get("/{user_id}", response_model=User)
def get_user(
    user_id: UUID,
    current_user: TokenData = Depends(require_user_read),
    db: Session = Depends(get_db)
):
    """Get user by ID."""
    user = UserService.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if user belongs to current tenant
    user_role = UserService.get_user_tenant_role(db, user_id, current_user.tenant_id)
    if not user_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in this tenant"
        )
    
    return user


@router.post("/", response_model=User)
async def create_user(
    user: UserCreate,
    current_user: TokenData = Depends(require_user_create),
    db: Session = Depends(get_db)
):
    """Create a new user in the current tenant."""
    # Check if user already exists
    existing_user = UserService.get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    new_user = UserService.create_user(db, user, current_user.tenant_id)
    return new_user


@router.put("/{user_id}", response_model=User)
def update_user(
    user_id: UUID,
    user_update: UserUpdate,
    current_user: TokenData = Depends(require_user_update),
    db: Session = Depends(get_db)
):
    """Update user."""
    # Check if user belongs to current tenant
    user_role = UserService.get_user_tenant_role(db, user_id, current_user.tenant_id)
    if not user_role:
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
    current_user: TokenData = Depends(require_user_delete),
    db: Session = Depends(get_db)
):
    """Delete user."""
    # Check if user belongs to current tenant
    user_role = UserService.get_user_tenant_role(db, user_id, current_user.tenant_id)
    if not user_role:
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
    
    success = UserService.delete_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "User deleted successfully"}


@router.post("/{user_id}/assign-role")
def assign_user_role(
    user_id: UUID,
    role_id: UUID,
    current_user: TokenData = Depends(require_user_update),
    db: Session = Depends(get_db)
):
    """Assign role to user."""
    # Check if user belongs to current tenant
    user_role = UserService.get_user_tenant_role(db, user_id, current_user.tenant_id)
    if not user_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in this tenant"
        )
    
    # Check if role belongs to current tenant
    role = db.query(app.models.Role).filter(
        app.models.Role.id == role_id,
        app.models.Role.tenant_id == current_user.tenant_id
    ).first()
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found in this tenant"
        )
    
    assignment = RoleService.assign_user_role(
        db, user_id, current_user.tenant_id, role_id, current_user.user_id
    )
    
    return {"message": "Role assigned successfully", "assignment_id": assignment.id}
