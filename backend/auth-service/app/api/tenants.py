from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.tenant import Tenant, TenantCreate, TenantUpdate, TenantWithStats
from app.schemas.auth import TokenData
from app.services.tenant_service import TenantService
from app.api.dependencies import get_current_user, require_tenant_read, require_tenant_update

router = APIRouter(prefix="/tenants", tags=["Tenants"])


@router.get("/current", response_model=TenantWithStats)
def get_current_tenant(
    current_user: TokenData = Depends(require_tenant_read),
    db: Session = Depends(get_db)
):
    """Get current tenant information."""
    tenant = TenantService.get_tenant(db, current_user.tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    stats = TenantService.get_tenant_stats(db, current_user.tenant_id)
    
    return TenantWithStats(
        **tenant.__dict__,
        **stats
    )


@router.put("/current", response_model=Tenant)
def update_current_tenant(
    tenant_update: TenantUpdate,
    current_user: TokenData = Depends(require_tenant_update),
    db: Session = Depends(get_db)
):
    """Update current tenant."""
    updated_tenant = TenantService.update_tenant(db, current_user.tenant_id, tenant_update)
    if not updated_tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    return updated_tenant


# These endpoints would typically be used by a super admin or system service
@router.get("/", response_model=List[Tenant])
def get_tenants(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=100),
    db: Session = Depends(get_db)
    # Note: This would need super admin permissions in a real system
):
    """Get all tenants (System admin only)."""
    tenants = TenantService.get_tenants(db, skip, limit)
    return tenants


@router.post("/", response_model=Tenant)
def create_tenant(
    tenant: TenantCreate,
    db: Session = Depends(get_db)
    # Note: This would need super admin permissions in a real system
):
    """Create a new tenant (System admin only)."""
    # Check if domain already exists
    existing_tenant = TenantService.get_tenant_by_domain(db, tenant.domain)
    if existing_tenant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant with this domain already exists"
        )
    
    new_tenant = TenantService.create_tenant(db, tenant)
    return new_tenant


@router.get("/{tenant_id}", response_model=TenantWithStats)
def get_tenant(
    tenant_id: UUID,
    db: Session = Depends(get_db)
    # Note: This would need super admin permissions in a real system
):
    """Get tenant by ID (System admin only)."""
    tenant = TenantService.get_tenant(db, tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    stats = TenantService.get_tenant_stats(db, tenant_id)
    
    return TenantWithStats(
        **tenant.__dict__,
        **stats
    )
