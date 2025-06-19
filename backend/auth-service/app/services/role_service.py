from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.models import Role, Permission, UserTenantRole
from app.schemas.role import RoleCreate, RoleUpdate


class RoleService:
    
    @staticmethod
    def create_role(db: Session, role: RoleCreate) -> Role:
        """Create a new role."""
        db_role = Role(
            tenant_id=role.tenant_id,
            name=role.name,
            description=role.description
        )
        db.add(db_role)
        db.flush()  # Get the ID before committing
        
        # Assign permissions to role
        if role.permission_ids:
            permissions = db.query(Permission).filter(Permission.id.in_(role.permission_ids)).all()
            db_role.permissions = permissions
        
        db.commit()
        db.refresh(db_role)
        return db_role
    
    @staticmethod
    def get_role(db: Session, role_id: UUID) -> Optional[Role]:
        """Get role by ID."""
        return db.query(Role).filter(Role.id == role_id).first()
    
    @staticmethod
    def get_tenant_roles(db: Session, tenant_id: UUID, skip: int = 0, limit: int = 100) -> List[Role]:
        """Get all roles for a tenant."""
        return db.query(Role).filter(
            Role.tenant_id == tenant_id,
            Role.is_active == True
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_role_by_name(db: Session, tenant_id: UUID, name: str) -> Optional[Role]:
        """Get role by name within a tenant."""
        return db.query(Role).filter(
            Role.tenant_id == tenant_id,
            Role.name == name
        ).first()
    
    @staticmethod
    def update_role(db: Session, role_id: UUID, role_update: RoleUpdate) -> Optional[Role]:
        """Update role."""
        db_role = db.query(Role).filter(Role.id == role_id).first()
        if not db_role:
            return None
        
        update_data = role_update.model_dump(exclude_unset=True, exclude={"permission_ids"})
        for field, value in update_data.items():
            setattr(db_role, field, value)
        
        # Update permissions if provided
        if role_update.permission_ids is not None:
            permissions = db.query(Permission).filter(Permission.id.in_(role_update.permission_ids)).all()
            db_role.permissions = permissions
        
        db.commit()
        db.refresh(db_role)
        return db_role
    
    @staticmethod
    def delete_role(db: Session, role_id: UUID) -> bool:
        """Delete role."""
        db_role = db.query(Role).filter(Role.id == role_id).first()
        if not db_role or db_role.is_system_role:
            return False
        
        # Check if role is assigned to any users
        user_count = db.query(UserTenantRole).filter(UserTenantRole.role_id == role_id).count()
        if user_count > 0:
            return False  # Cannot delete role that is assigned to users
        
        db.delete(db_role)
        db.commit()
        return True
    
    @staticmethod
    def assign_user_role(db: Session, user_id: UUID, tenant_id: UUID, role_id: UUID, assigned_by: UUID) -> UserTenantRole:
        """Assign a role to a user in a tenant."""
        # Check if user already has a role in this tenant
        existing = db.query(UserTenantRole).filter(
            UserTenantRole.user_id == user_id,
            UserTenantRole.tenant_id == tenant_id
        ).first()
        
        if existing:
            # Update existing role
            existing.role_id = role_id
            existing.assigned_by = assigned_by
            db.commit()
            db.refresh(existing)
            return existing
        else:
            # Create new assignment
            assignment = UserTenantRole(
                user_id=user_id,
                tenant_id=tenant_id,
                role_id=role_id,
                assigned_by=assigned_by
            )
            db.add(assignment)
            db.commit()
            db.refresh(assignment)
            return assignment
    
    @staticmethod
    def remove_user_role(db: Session, user_id: UUID, tenant_id: UUID) -> bool:
        """Remove user's role from a tenant."""
        assignment = db.query(UserTenantRole).filter(
            UserTenantRole.user_id == user_id,
            UserTenantRole.tenant_id == tenant_id
        ).first()
        
        if not assignment:
            return False
        
        db.delete(assignment)
        db.commit()
        return True
    
    @staticmethod
    def get_user_permissions(db: Session, user_id: UUID, tenant_id: UUID) -> List[str]:
        """Get all permissions for a user in a tenant."""
        assignment = db.query(UserTenantRole).filter(
            UserTenantRole.user_id == user_id,
            UserTenantRole.tenant_id == tenant_id
        ).first()
        
        if not assignment:
            return []
        
        role = db.query(Role).filter(Role.id == assignment.role_id).first()
        if not role:
            return []
        
        return [perm.name for perm in role.permissions]
    
    @staticmethod
    def create_default_super_admin_role(db: Session, tenant_id: UUID) -> Role:
        """Create default super admin role for a tenant."""
        # Get all permissions
        all_permissions = db.query(Permission).all()
        
        role = Role(
            tenant_id=tenant_id,
            name="Super Admin",
            description="Default super administrator role with all permissions",
            is_system_role=True,
            permissions=all_permissions
        )
        
        db.add(role)
        db.commit()
        db.refresh(role)
        return role
