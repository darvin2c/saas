from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class PermissionBase(BaseModel):
    name: str
    description: Optional[str] = None
    resource: str
    action: str


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[str] = None


class PermissionInDB(PermissionBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class Permission(PermissionInDB):
    pass
