"""
Admin routes: user management, teacher verification, reported notes, and
platform-wide statistics. All routes require the 'admin' role.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models.note import Note
from app.models.user import User, UserRole
from app.models.group import StudyGroup
from app.models.chat import AIChat
from app.schemas.user_schema import UserOut
from app.utils.dependencies import require_admin

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return db.query(User).order_by(User.created_at.desc()).all()


@router.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return None


@router.put("/users/{user_id}/verify-teacher", response_model=UserOut)
def verify_teacher(user_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.role != UserRole.teacher:
        raise HTTPException(status_code=400, detail="Only teacher accounts can be verified")

    user.is_verified_teacher = True
    db.commit()
    db.refresh(user)
    return user


@router.put("/users/{user_id}/deactivate", response_model=UserOut)
def deactivate_user(user_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    db.commit()
    db.refresh(user)
    return user


@router.get("/notes/reported")
def get_reported_notes(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return db.query(Note).filter(Note.is_reported == True).all()  # noqa: E712


@router.put("/notes/{note_id}/report", status_code=200)
def report_note(note_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    note.is_reported = True
    db.commit()
    return {"message": "Note flagged as reported"}


@router.delete("/notes/{note_id}", status_code=204)
def admin_delete_note(note_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(note)
    db.commit()
    return None


@router.get("/statistics")
def get_statistics(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    """High-level platform statistics for the admin dashboard."""
    total_users = db.query(User).count()
    total_students = db.query(User).filter(User.role == UserRole.student).count()
    total_teachers = db.query(User).filter(User.role == UserRole.teacher).count()
    total_notes = db.query(Note).count()
    total_groups = db.query(StudyGroup).count()
    total_ai_chats = db.query(AIChat).count()
    reported_notes = db.query(Note).filter(Note.is_reported == True).count()  # noqa: E712

    return {
        "total_users": total_users,
        "total_students": total_students,
        "total_teachers": total_teachers,
        "total_notes": total_notes,
        "total_study_groups": total_groups,
        "total_ai_chats": total_ai_chats,
        "reported_notes": reported_notes,
    }
