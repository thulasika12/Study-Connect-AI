"""
User profile routes.
"""
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models.user import User
from app.schemas.user_schema import UserOut, UserUpdate
from app.services.file_service import save_upload_file
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/profile", response_model=UserOut)
def get_profile(current_user: User = Depends(get_current_user)):
    """Returns the currently authenticated user's profile."""
    return current_user


@router.put("/profile", response_model=UserOut)
def update_profile(
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Updates editable profile fields for the current user."""
    if payload.name is not None:
        current_user.name = payload.name
    if payload.bio is not None:
        current_user.bio = payload.bio
    if payload.profile_image is not None:
        current_user.profile_image = payload.profile_image

    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/profile/avatar", response_model=UserOut)
def upload_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Uploads a new profile image for the current user."""
    url = save_upload_file(file, category="profile")
    current_user.profile_image = url
    db.commit()
    db.refresh(current_user)
    return current_user
