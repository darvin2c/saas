from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import User, Tenant, UserTenant
from app.schemas.user import UserCreate, UserUpdate
from app.utils.auth import get_password_hash, generate_reset_token


class UserService:
    
    @staticmethod
    def create_user(db: Session, user: UserCreate, tenant_id: UUID) -> User:
        """Create a new user."""
        hashed_password = get_password_hash(user.password)
        
        db_user = User(
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            hashed_password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def get_user(db: Session, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email."""
        return db.query(User).filter(User.email == email).first()
    

    @staticmethod
    def get_user_by_reset_token(db: Session, token: str) -> Optional[User]:
        """Get user by reset password token."""
        return db.query(User).filter(
            User.reset_password_token == token,
            User.reset_password_expires > datetime.utcnow()
        ).first()
    
    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination."""
        return db.query(User).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_tenant_users(db: Session, tenant_id: UUID, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users for a tenant."""
        return db.query(User).join(UserTenant).filter(
            UserTenant.tenant_id == tenant_id
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_user(db: Session, user_id: UUID, user_update: UserUpdate) -> Optional[User]:
        """Update user."""
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return None
        
        update_data = user_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def delete_user(db: Session, user_id: UUID) -> bool:
        """Delete user."""
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return False
        
        db.delete(db_user)
        db.commit()
        return True
    

    @staticmethod
    def initiate_password_reset(db: Session, email: str, tenant_domain: str) -> Optional[User]:
        """Initiate password reset process."""
        user = UserService.get_user_by_email(db, email)
        if not user:
            return None
        
        # Check if user belongs to the tenant
        tenant = db.query(Tenant).filter(Tenant.domain == tenant_domain).first()
        if not tenant:
            return None
        
        user_tenant = db.query(UserTenant).filter(
            UserTenant.user_id == user.id,
            UserTenant.tenant_id == tenant.id
        ).first()
        
        if not user_tenant:
            return None
        
        reset_token = generate_reset_token()
        reset_expires = datetime.utcnow() + timedelta(hours=1)
        
        user.reset_password_token = reset_token
        user.reset_password_expires = reset_expires
        db.commit()
        
        return user
    
    @staticmethod
    def reset_password(db: Session, token: str, new_password: str) -> bool:
        """Reset user password with token."""
        user = UserService.get_user_by_reset_token(db, token)
        if not user:
            return False
        
        user.hashed_password = get_password_hash(new_password)
        user.reset_password_token = None
        user.reset_password_expires = None
        db.commit()
        return True


    
    @staticmethod
    def update_last_login(db: Session, user_id: UUID) -> None:
        """Update user's last login timestamp."""
        db.query(User).filter(User.id == user_id).update({
            "last_login": datetime.utcnow()
        })
        db.commit()
    
    @staticmethod
    def check_user_in_tenant(db: Session, user_id: UUID, tenant_id: UUID) -> bool:
        """Check if a user belongs to a tenant."""
        user_tenant = db.query(UserTenant).filter(
            UserTenant.user_id == user_id,
            UserTenant.tenant_id == tenant_id
        ).first()
        
        return user_tenant is not None
        
    @staticmethod
    def change_password(db: Session, user_id: UUID, current_password: str, new_password: str) -> bool:
        """Change user password if current password is correct."""
        from app.utils.auth import verify_password, get_password_hash
        
        user = UserService.get_user(db, user_id)
        if not user:
            return False
            
        # Verify current password
        if not verify_password(current_password, user.hashed_password):
            return False
            
        # Update password
        user.hashed_password = get_password_hash(new_password)
        db.commit()
        return True
