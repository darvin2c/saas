from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.auth import (
    UserLogin, UserRegister, Token, RefreshToken, 
    PasswordReset, PasswordResetConfirm, PasswordChange
)
from app.services.auth_service import AuthService
from app.api.dependencies import get_current_user

router = APIRouter(tags=["Authentication"])


@router.post("/register", response_model=dict)
async def register_user(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """Register a new user."""
    try:
        result = await AuthService.register_user(db, user_data)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
def login_user(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """Login user and return JWT tokens."""
    user = AuthService.authenticate_user(db, login_data)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    #if not user.is_verified:
    #    raise HTTPException(
    #        status_code=status.HTTP_401_UNAUTHORIZED,
    #        detail="Email not verified"
    #    )
    
    tokens = AuthService.create_user_tokens(user.id)
    
    return tokens


@router.post("/refresh", response_model=Token)
def refresh_token(
    refresh_data: RefreshToken,
    db: Session = Depends(get_db)
):
    """Refresh access token."""
    tokens = AuthService.refresh_access_token(db, refresh_data.refresh_token)
    
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    return tokens



@router.post("/request-password-reset")
async def request_password_reset(
    reset_data: PasswordReset,
    db: Session = Depends(get_db)
):
    """Request password reset."""
    success = await AuthService.request_password_reset(
        db, reset_data.email, reset_data.tenant_domain
    )
    
    # Always return success to prevent email enumeration
    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/reset-password")
def reset_password(
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """Reset password with token."""
    success = AuthService.reset_password(db, reset_data.token, reset_data.new_password)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    return {"message": "Password reset successfully"}


@router.post("/change-password")
def change_password(
    password_data: PasswordChange,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change password for authenticated user."""
    success = AuthService.change_password(
        db, 
        current_user.user_id, 
        password_data.current_password, 
        password_data.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    return {"message": "Password changed successfully"}
