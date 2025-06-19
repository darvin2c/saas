from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    tenant_id: UUID
    permission_ids: List[UUID] = []


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    permission_ids: Optional[List[UUID]] = None


class RoleInDB(RoleBase):
    id: UUID
    tenant_id: UUID
    is_system_role: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Role(RoleInDB):
    pass


class RoleWithPermissions(RoleInDB):
    permissions: List["Permission"] = []


class UserRoleAssignment(BaseModel):
    user_id: UUID
    tenant_id: UUID
    role_id: UUID


# Import Permission here to avoid circular imports
from .permission import Permission
RoleWithPermissions.model_rebuild()
