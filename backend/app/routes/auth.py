"""
Authentication routes: register, login, forgot password, reset password.
"""
import secrets

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models.user import User
from app.schemas.user_schema import (
    UserRegister,
    UserLogin,
    Token,
    UserOut,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)
from app.services.auth_service import register_user, authenticate_user, build_token_for_user
from app.services.email_service import send_password_reset_email, send_welcome_email
from app.config.security import hash_password

router = APIRouter(prefix="/auth", tags=["Authentication"])


_reset_tokens: dict[str, str] = {}


@router.post("/register", response_model=Token, status_code=201)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    """Create a new student/teacher account and return a JWT token."""
    user = register_user(db, payload)
    send_welcome_email(user.email, user.name)
    token = build_token_for_user(user)
    return Token(access_token=token, user=UserOut.model_validate(user))


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    """Validate credentials and issue a JWT access token."""
    user = authenticate_user(db, payload)
    token = build_token_for_user(user)
    return Token(access_token=token, user=UserOut.model_validate(user))


@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Generates a reset token and 'sends' (logs) a reset email."""
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        # Don't reveal whether the email exists
        return {"message": "If that email exists, a reset link has been sent."}

    reset_token = secrets.token_urlsafe(32)
    _reset_tokens[payload.email] = reset_token
    send_password_reset_email(payload.email, reset_token)
    return {"message": "If that email exists, a reset link has been sent."}


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Verifies the reset token and updates the user's password."""
    stored_token = _reset_tokens.get(payload.email)
    if not stored_token or stored_token != payload.reset_token:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password = hash_password(payload.new_password)
    db.commit()
    del _reset_tokens[payload.email]
    return {"message": "Password has been reset successfully"}
