from typing import Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from app.models import User, Tenant, UserTenantRole
from app.schemas.auth import UserLogin, UserRegister, Token, TokenData
from app.services.user_service import UserService
from app.services.tenant_service import TenantService
from app.services.role_service import RoleService
from app.utils.auth import verify_password, create_access_token, create_refresh_token, verify_token
from app.utils.email import send_verification_email


class AuthService:
    
    @staticmethod
    async def register_user(db: Session, user_data: UserRegister) -> Dict[str, Any]:
        """Register a new user."""
        # Check if tenant exists
        tenant = TenantService.get_tenant_by_domain(db, user_data.tenant_domain)
        if not tenant:
            raise ValueError("Tenant not found")
        
        if not tenant.is_active:
            raise ValueError("Tenant is not active")
        
        # Check if user already exists
        existing_user = UserService.get_user_by_email(db, user_data.email)
        if existing_user:
            # Check if user already belongs to this tenant
            existing_assignment = db.query(UserTenantRole).filter(
                UserTenantRole.user_id == existing_user.id,
                UserTenantRole.tenant_id == tenant.id
            ).first()
            
            if existing_assignment:
                raise ValueError("User already exists in this tenant")
        
        # Create user if doesn't exist
        if not existing_user:
            user = UserService.create_user(db, user_data, tenant.id)
        else:
            user = existing_user
        
        # Send verification email
        await send_verification_email(user.email, user.verification_token, tenant.domain)
        
        return {
            "message": "User registered successfully. Please check your email for verification.",
            "user_id": user.id,
            "requires_verification": not user.is_verified
        }
    
    @staticmethod
    def authenticate_user(db: Session, login_data: UserLogin) -> Optional[Dict[str, Any]]:
        """Authenticate user and return user info with tenant context."""
        # Get user
        user = UserService.get_user_by_email(db, login_data.email)
        if not user or not user.is_active:
            return None
        
        # Verify password
        if not verify_password(login_data.password, user.hashed_password):
            return None
        
        # Get user's primary tenant (first active tenant)
        user_tenant_roles = db.query(UserTenantRole).filter(
            UserTenantRole.user_id == user.id
        ).all()
        
        if not user_tenant_roles:
            return None
        
        # Find first active tenant
        for user_tenant_role in user_tenant_roles:
            tenant = TenantService.get_tenant(db, user_tenant_role.tenant_id)
            if tenant and tenant.is_active:
                # Update last login
                UserService.update_last_login(db, user.id)
                
                return {
                    "user": user,
                    "tenant": tenant,
                    "role_info": user_tenant_role
                }
        
        # No active tenant found
        return None
    
    @staticmethod
    def create_user_tokens(user_id: UUID, tenant_id: UUID, permissions: list[str]) -> Token:
        """Create access and refresh tokens for user."""
        token_data = {
            "sub": str(user_id),
            "tenant_id": str(tenant_id),
            "permissions": permissions
        }
        
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token({"sub": str(user_id), "tenant_id": str(tenant_id)})
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token
        )
    
    @staticmethod
    def refresh_access_token(db: Session, refresh_token: str) -> Optional[Token]:
        """Create new access token from refresh token."""
        payload = verify_token(refresh_token, "refresh")
        if not payload:
            return None
        
        user_id = UUID(payload.get("sub"))
        tenant_id = UUID(payload.get("tenant_id"))
        
        # Verify user and tenant are still valid
        user = UserService.get_user(db, user_id)
        if not user or not user.is_active:
            return None
        
        tenant = TenantService.get_tenant(db, tenant_id)
        if not tenant or not tenant.is_active:
            return None
        
        # Get current permissions
        permissions = RoleService.get_user_permissions(db, user_id, tenant_id)
        
        return AuthService.create_user_tokens(user_id, tenant_id, permissions)
    
    @staticmethod
    def verify_access_token(db: Session, token: str) -> Optional[TokenData]:
        """Verify access token and return token data."""
        payload = verify_token(token, "access")
        if not payload:
            return None
        
        user_id = UUID(payload.get("sub"))
        tenant_id = UUID(payload.get("tenant_id"))
        permissions = payload.get("permissions", [])
        
        # Verify user and tenant are still valid
        user = UserService.get_user(db, user_id)
        if not user or not user.is_active:
            return None
        
        tenant = TenantService.get_tenant(db, tenant_id)
        if not tenant or not tenant.is_active:
            return None
        
        return TokenData(
            user_id=user_id,
            tenant_id=tenant_id,
            permissions=permissions
        )
    
    @staticmethod
    async def verify_email(db: Session, token: str) -> bool:
        """Verify user email."""
        return UserService.verify_user_email(db, token)
    
    @staticmethod
    async def request_password_reset(db: Session, email: str, tenant_domain: str) -> bool:
        """Request password reset."""
        user = UserService.initiate_password_reset(db, email, tenant_domain)
        if not user:
            return False
        
        # Send reset email
        from app.utils.email import send_reset_password_email
        await send_reset_password_email(user.email, user.reset_password_token, tenant_domain)
        return True
    
    @staticmethod
    def reset_password(db: Session, token: str, new_password: str) -> bool:
        """Reset user password."""
        return UserService.reset_password(db, token, new_password)
