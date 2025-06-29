from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID


class UserTenantBase(BaseModel):
    user_id: UUID
    tenant_id: UUID


class UserTenantCreate(UserTenantBase):
    pass


class UserTenantInDB(UserTenantBase):
    id: UUID
    assigned_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserTenant(UserTenantInDB):
    pass
