from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.tenant import Tenant, TenantCreate, TenantUpdate, TenantWithStats
from app.schemas.auth import TokenData
from app.services.tenant_service import TenantService
from app.services.user_service import UserService
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/tenants", tags=["Tenants"])


@router.get("/exists", response_model=dict)
async def check_domain(domain: str = Query(..., description="Tenant domain to check"), db: Session = Depends(get_db)):
    """Check if tenant domain exists."""
    tenant = TenantService.get_tenant_by_domain(db, domain)
    return {"exists": tenant is not None}


@router.get("/by-id/{tenant_id}", response_model=TenantWithStats)
def get_tenant_by_id(
    tenant_id: UUID,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get tenant information by ID."""
    # Check if user belongs to the tenant
    if not UserService.check_user_in_tenant(db, current_user.user_id, tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not belong to this tenant"
        )
    
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


@router.patch("/{tenant_id}", response_model=Tenant)
def update_tenant(
    tenant_id: UUID,
    tenant_update: TenantUpdate,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update tenant partially."""
    # Check if user belongs to the tenant
    if not UserService.check_user_in_tenant(db, current_user.user_id, tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not belong to this tenant"
        )
    
    updated_tenant = TenantService.update_tenant(db, tenant_id, tenant_update)
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
