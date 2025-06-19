from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.models import Permission
from app.schemas.permission import PermissionCreate, PermissionUpdate


class PermissionService:
    
    @staticmethod
    def create_permission(db: Session, permission: PermissionCreate) -> Permission:
        """Create a new permission."""
        db_permission = Permission(
            name=permission.name,
            description=permission.description,
            resource=permission.resource,
            action=permission.action
        )
        db.add(db_permission)
        db.commit()
        db.refresh(db_permission)
        return db_permission
    
    @staticmethod
    def get_permission(db: Session, permission_id: UUID) -> Optional[Permission]:
        """Get permission by ID."""
        return db.query(Permission).filter(Permission.id == permission_id).first()
    
    @staticmethod
    def get_permission_by_name(db: Session, name: str) -> Optional[Permission]:
        """Get permission by name."""
        return db.query(Permission).filter(Permission.name == name).first()
    
    @staticmethod
    def get_permissions(db: Session, skip: int = 0, limit: int = 100) -> List[Permission]:
        """Get all permissions with pagination."""
        return db.query(Permission).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_permissions_by_resource(db: Session, resource: str) -> List[Permission]:
        """Get permissions by resource."""
        return db.query(Permission).filter(Permission.resource == resource).all()
    
    @staticmethod
    def update_permission(db: Session, permission_id: UUID, permission_update: PermissionUpdate) -> Optional[Permission]:
        """Update permission."""
        db_permission = db.query(Permission).filter(Permission.id == permission_id).first()
        if not db_permission:
            return None
        
        update_data = permission_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_permission, field, value)
        
        db.commit()
        db.refresh(db_permission)
        return db_permission
    
    @staticmethod
    def delete_permission(db: Session, permission_id: UUID) -> bool:
        """Delete permission."""
        db_permission = db.query(Permission).filter(Permission.id == permission_id).first()
        if not db_permission:
            return False
        
        db.delete(db_permission)
        db.commit()
        return True
    
    @staticmethod
    def create_default_permissions(db: Session) -> List[Permission]:
        """Create default system permissions."""
        default_permissions = [
            # User management
            {"name": "users:create", "resource": "users", "action": "create", "description": "Create users"},
            {"name": "users:read", "resource": "users", "action": "read", "description": "View users"},
            {"name": "users:update", "resource": "users", "action": "update", "description": "Update users"},
            {"name": "users:delete", "resource": "users", "action": "delete", "description": "Delete users"},
            
            # Role management
            {"name": "roles:create", "resource": "roles", "action": "create", "description": "Create roles"},
            {"name": "roles:read", "resource": "roles", "action": "read", "description": "View roles"},
            {"name": "roles:update", "resource": "roles", "action": "update", "description": "Update roles"},
            {"name": "roles:delete", "resource": "roles", "action": "delete", "description": "Delete roles"},
            
            # Permission management
            {"name": "permissions:read", "resource": "permissions", "action": "read", "description": "View permissions"},
            
            # Tenant management
            {"name": "tenant:read", "resource": "tenant", "action": "read", "description": "View tenant info"},
            {"name": "tenant:update", "resource": "tenant", "action": "update", "description": "Update tenant info"},
        ]
        
        created_permissions = []
        for perm_data in default_permissions:
            existing = db.query(Permission).filter(Permission.name == perm_data["name"]).first()
            if not existing:
                permission = Permission(**perm_data)
                db.add(permission)
                created_permissions.append(permission)
        
        if created_permissions:
            db.commit()
            for perm in created_permissions:
                db.refresh(perm)
        
        return created_permissions
