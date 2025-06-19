from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.role import Role, RoleCreate, RoleUpdate, RoleWithPermissions, UserRoleAssignment
from app.schemas.auth import TokenData
from app.services.role_service import RoleService
from app.api.dependencies import (
    get_current_user, require_role_read, require_role_create, 
    require_role_update, require_role_delete
)

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.get("/", response_model=List[RoleWithPermissions])
def get_roles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=100),
    current_user: TokenData = Depends(require_role_read),
    db: Session = Depends(get_db)
):
    """Get all roles for the current tenant."""
    roles = RoleService.get_tenant_roles(db, current_user.tenant_id, skip, limit)
    
    # Load permissions for each role
    roles_with_permissions = []
    for role in roles:
        role_dict = role.__dict__.copy()
        role_dict["permissions"] = role.permissions
        roles_with_permissions.append(RoleWithPermissions(**role_dict))
    
    return roles_with_permissions


@router.get("/{role_id}", response_model=RoleWithPermissions)
def get_role(
    role_id: UUID,
    current_user: TokenData = Depends(require_role_read),
    db: Session = Depends(get_db)
):
    """Get role by ID."""
    role = RoleService.get_role(db, role_id)
    if not role or role.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    role_dict = role.__dict__.copy()
    role_dict["permissions"] = role.permissions
    return RoleWithPermissions(**role_dict)


@router.post("/", response_model=Role)
def create_role(
    role: RoleCreate,
    current_user: TokenData = Depends(require_role_create),
    db: Session = Depends(get_db)
):
    """Create a new role."""
    # Ensure role is created for current tenant
    role.tenant_id = current_user.tenant_id
    
    # Check if role name already exists in tenant
    existing_role = RoleService.get_role_by_name(db, current_user.tenant_id, role.name)
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role with this name already exists in tenant"
        )
    
    new_role = RoleService.create_role(db, role)
    return new_role


@router.put("/{role_id}", response_model=Role)
def update_role(
    role_id: UUID,
    role_update: RoleUpdate,
    current_user: TokenData = Depends(require_role_update),
    db: Session = Depends(get_db)
):
    """Update role."""
    role = RoleService.get_role(db, role_id)
    if not role or role.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    # Cannot update system roles
    if role.is_system_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update system role"
        )
    
    updated_role = RoleService.update_role(db, role_id, role_update)
    return updated_role


@router.delete("/{role_id}")
def delete_role(
    role_id: UUID,
    current_user: TokenData = Depends(require_role_delete),
    db: Session = Depends(get_db)
):
    """Delete role."""
    role = RoleService.get_role(db, role_id)
    if not role or role.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    # Cannot delete system roles
    if role.is_system_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete system role"
        )
    
    success = RoleService.delete_role(db, role_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete role that is assigned to users"
        )
    
    return {"message": "Role deleted successfully"}


@router.post("/assign-user", response_model=dict)
def assign_user_to_role(
    assignment: UserRoleAssignment,
    current_user: TokenData = Depends(require_role_update),
    db: Session = Depends(get_db)
):
    """Assign a user to a role."""
    # Ensure assignment is for current tenant
    if assignment.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot assign roles in different tenant"
        )
    
    # Verify role exists and belongs to tenant
    role = RoleService.get_role(db, assignment.role_id)
    if not role or role.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    # Verify user exists and belongs to tenant
    from app.services.user_service import UserService
    user_role = UserService.get_user_tenant_role(db, assignment.user_id, current_user.tenant_id)
    if not user_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in this tenant"
        )
    
    role_assignment = RoleService.assign_user_role(
        db, assignment.user_id, assignment.tenant_id, assignment.role_id, current_user.user_id
    )
    
    return {
        "message": "User assigned to role successfully",
        "assignment_id": role_assignment.id
    }


@router.delete("/unassign-user/{user_id}")
def unassign_user_from_role(
    user_id: UUID,
    current_user: TokenData = Depends(require_role_update),
    db: Session = Depends(get_db)
):
    """Remove user's role assignment."""
    success = RoleService.remove_user_role(db, user_id, current_user.tenant_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User role assignment not found"
        )
    
    return {"message": "User role assignment removed successfully"}
