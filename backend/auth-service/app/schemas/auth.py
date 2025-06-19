from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID


class UserLogin(BaseModel):
    email: EmailStr
    password: str
    tenant_domain: str


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    tenant_domain: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[UUID] = None
    tenant_id: Optional[UUID] = None
    permissions: list[str] = []


class RefreshToken(BaseModel):
    refresh_token: str


class PasswordReset(BaseModel):
    email: EmailStr
    tenant_domain: str


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


class EmailVerification(BaseModel):
    token: str
