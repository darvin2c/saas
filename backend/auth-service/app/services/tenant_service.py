from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Tenant, User, UserTenant
from app.schemas.tenant import TenantCreate, TenantUpdate


class TenantService:
    
    @staticmethod
    def create_tenant(db: Session, tenant: TenantCreate) -> Tenant:
        """Create a new tenant."""
        db_tenant = Tenant(
            name=tenant.name,
            domain=tenant.domain,
            description=tenant.description
        )
        db.add(db_tenant)
        db.commit()
        db.refresh(db_tenant)
        
        return db_tenant
    
    @staticmethod
    def get_tenant(db: Session, tenant_id: UUID) -> Optional[Tenant]:
        """Get tenant by ID."""
        return db.query(Tenant).filter(Tenant.id == tenant_id).first()
    
    @staticmethod
    def get_tenant_by_domain(db: Session, domain: str) -> Optional[Tenant]:
        """Get tenant by domain."""
        return db.query(Tenant).filter(Tenant.domain == domain).first()
    
    @staticmethod
    def get_tenants(db: Session, skip: int = 0, limit: int = 100) -> List[Tenant]:
        """Get all tenants with pagination."""
        return db.query(Tenant).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_tenant(db: Session, tenant_id: UUID, tenant_update: TenantUpdate) -> Optional[Tenant]:
        """Update tenant."""
        db_tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not db_tenant:
            return None
        
        update_data = tenant_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_tenant, field, value)
        
        db.commit()
        db.refresh(db_tenant)
        return db_tenant
    
    @staticmethod
    def delete_tenant(db: Session, tenant_id: UUID) -> bool:
        """Delete tenant."""
        db_tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not db_tenant:
            return False
        
        db.delete(db_tenant)
        db.commit()
        return True
    
    @staticmethod
    def get_tenant_stats(db: Session, tenant_id: UUID) -> dict:
        """Get tenant statistics."""
        user_count = db.query(func.count(UserTenant.user_id.distinct())).filter(
            UserTenant.tenant_id == tenant_id
        ).scalar()
        
        return {
            "user_count": user_count or 0
        }
