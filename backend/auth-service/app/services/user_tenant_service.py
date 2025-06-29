from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.models import User, Tenant, UserTenant
from app.schemas.user_tenant import UserTenantCreate


class UserTenantService:
    
    @staticmethod
    def create_user_tenant(db: Session, user_tenant: UserTenantCreate) -> UserTenant:
        """Assign a user to a tenant."""
        db_user_tenant = UserTenant(
            user_id=user_tenant.user_id,
            tenant_id=user_tenant.tenant_id
        )
        db.add(db_user_tenant)
        db.commit()
        db.refresh(db_user_tenant)
        return db_user_tenant
    
    @staticmethod
    def get_user_tenant(db: Session, user_id: UUID, tenant_id: UUID) -> Optional[UserTenant]:
        """Get user-tenant relationship."""
        return db.query(UserTenant).filter(
            UserTenant.user_id == user_id,
            UserTenant.tenant_id == tenant_id
        ).first()
    
    @staticmethod
    def get_tenant_users(db: Session, tenant_id: UUID, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users for a tenant."""
        return db.query(User).join(UserTenant).filter(
            UserTenant.tenant_id == tenant_id
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_user_tenants(db: Session, user_id: UUID) -> List[Tenant]:
        """Get all tenants for a user."""
        return db.query(Tenant).join(UserTenant).filter(
            UserTenant.user_id == user_id
        ).all()
    
    @staticmethod
    def delete_user_tenant(db: Session, user_id: UUID, tenant_id: UUID) -> bool:
        """Remove user from tenant."""
        db_user_tenant = db.query(UserTenant).filter(
            UserTenant.user_id == user_id,
            UserTenant.tenant_id == tenant_id
        ).first()
        
        if not db_user_tenant:
            return False
        
        db.delete(db_user_tenant)
        db.commit()
        return True
