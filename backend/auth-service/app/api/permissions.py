from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.permission import Permission, PermissionCreate, PermissionUpdate
from app.schemas.auth import TokenData
from app.services.permission_service import PermissionService
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/permissions", tags=["Permissions"])


@router.get("/", response_model=List[Permission])
def get_permissions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=100),
    resource: str = Query(None, description="Filter by resource"),
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all permissions."""
    if resource:
        permissions = PermissionService.get_permissions_by_resource(db, resource)
    else:
        permissions = PermissionService.get_permissions(db, skip, limit)
    
    return permissions


@router.get("/{permission_id}", response_model=Permission)
def get_permission(
    permission_id: UUID,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get permission by ID."""
    permission = PermissionService.get_permission(db, permission_id)
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )
    
    return permission


@router.post("/", response_model=Permission)
def create_permission(
    permission: PermissionCreate,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new permission (System admin only)."""
    # In a real system, this would require super admin permissions
    
    # Check if permission name already exists
    existing_permission = PermissionService.get_permission_by_name(db, permission.name)
    if existing_permission:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Permission with this name already exists"
        )
    
    new_permission = PermissionService.create_permission(db, permission)
    return new_permission


@router.put("/{permission_id}", response_model=Permission)
def update_permission(
    permission_id: UUID,
    permission_update: PermissionUpdate,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update permission (System admin only)."""
    # In a real system, this would require super admin permissions
    
    updated_permission = PermissionService.update_permission(db, permission_id, permission_update)
    if not updated_permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )
    
    return updated_permission


@router.delete("/{permission_id}")
def delete_permission(
    permission_id: UUID,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete permission (System admin only)."""
    # In a real system, this would require super admin permissions
    
    success = PermissionService.delete_permission(db, permission_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )
    
    return {"message": "Permission deleted successfully"}


@router.post("/initialize-defaults")
def initialize_default_permissions(
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Initialize default system permissions."""
    # In a real system, this would require super admin permissions
    
    created_permissions = PermissionService.create_default_permissions(db)
    
    return {
        "message": f"Initialized {len(created_permissions)} default permissions",
        "permissions": [p.name for p in created_permissions]
    }
