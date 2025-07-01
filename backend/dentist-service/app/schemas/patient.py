from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime, date
from uuid import UUID


class PatientBase(BaseModel):
    first_name: str
    last_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    address: Optional[str] = None
    medical_history: Optional[str] = None


class PatientCreate(PatientBase):
    tenant_id: UUID


class PatientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    address: Optional[str] = None
    medical_history: Optional[str] = None
    is_active: Optional[bool] = None


class PatientInDB(PatientBase):
    id: UUID
    tenant_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Patient(PatientInDB):
    pass
