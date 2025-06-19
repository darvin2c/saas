from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class TenantBase(BaseModel):
    name: str
    domain: str
    description: Optional[str] = None


class TenantCreate(TenantBase):
    pass


class TenantUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class TenantInDB(TenantBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Tenant(TenantInDB):
    pass


class TenantWithStats(TenantInDB):
    user_count: int = 0
    role_count: int = 0
