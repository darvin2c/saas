from typing import Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from app.models import User, UserTenant
from app.schemas.auth import UserRegister, Token, TokenData, UserLogin
from app.schemas.tenant import TenantCreate
from app.services.user_service import UserService
from app.services.tenant_service import TenantService
from app.services.user_tenant_service import UserTenantService
from app.utils.auth import verify_password, create_access_token, create_refresh_token, verify_token


class AuthService:
    
    @staticmethod
    async def register_user(db: Session, user_data: UserRegister) -> Dict[str, Any]:
        """Register a new user."""
        # Check if tenant exists
        tenant = TenantService.get_tenant_by_domain(db, user_data.tenant_domain)
        if not tenant:
            # Create new tenant with provided name and domain
            tenant_data = TenantCreate(
                name=user_data.tenant_name,
                domain=user_data.tenant_domain,
                description=f"Tenant created during registration by {user_data.email}"
            )
            tenant = TenantService.create_tenant(db, tenant_data)
        elif not tenant.is_active:
            raise ValueError("Tenant is not active")
        
        # Check if user already exists
        existing_user = UserService.get_user_by_email(db, user_data.email)
        if existing_user:
            # Check if user already belongs to this tenant
            existing_assignment = db.query(UserTenant).filter(
                UserTenant.user_id == existing_user.id,
                UserTenant.tenant_id == tenant.id
            ).first()
            
            if existing_assignment:
                raise ValueError("User already exists in this tenant")
        
        # Create user if doesn't exist
        if not existing_user:
            user = UserService.create_user(db, user_data, tenant.id)
        else:
            user = existing_user
            
        # Create user-tenant relationship
        from app.schemas.user_tenant import UserTenantCreate
        user_tenant_data = UserTenantCreate(
            user_id=user.id,
            tenant_id=tenant.id
        )
        UserTenantService.create_user_tenant(db, user_tenant_data)
        
        return {
            "message": "User registered successfully.",
            "user_id": user.id,
            "requires_verification": False
        }
    
    @staticmethod
    def authenticate_user(db: Session, login_data: UserLogin) -> Optional[User]:
        """Authenticate user and return user if credentials are valid."""
        # Get user
        user = UserService.get_user_by_email(db, login_data.email)
        if not user or not user.is_active:
            return None
        
        # Verify password
        if not verify_password(login_data.password, user.hashed_password):
            return None
        
        # Update last login
        UserService.update_last_login(db, user.id)
        
        return user
    
    @staticmethod
    def create_user_tokens(user_id: UUID) -> Token:
        """Create access and refresh tokens for user."""
        token_data = {
            "sub": str(user_id)
        }
        
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token({"sub": str(user_id)})
        
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
        
        # Verify user is still valid
        user = UserService.get_user(db, user_id)
        if not user or not user.is_active:
            return None
        
        return AuthService.create_user_tokens(user_id)
    
    @staticmethod
    def verify_access_token(db: Session, token: str) -> Optional[TokenData]:
        """Verify access token and return token data."""
        payload = verify_token(token, "access")
        if not payload:
            return None
        
        user_id = UUID(payload.get("sub"))
        
        # Verify user is still valid
        user = UserService.get_user(db, user_id)
        if not user or not user.is_active:
            return None
        
        return TokenData(user_id=user_id)
    

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
