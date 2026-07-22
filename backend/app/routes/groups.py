"""
Study group routes: create, list, join, and post/read discussion messages.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.config.database import get_db
from app.models.group import StudyGroup, GroupMember, GroupDiscussion
from app.models.user import User
from app.schemas.note_schema import GroupCreate, GroupOut, DiscussionCreate, DiscussionOut
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/groups", tags=["Study Groups"])


def _serialize_group(group: StudyGroup) -> GroupOut:
    data = GroupOut.model_validate(group)
    data.member_count = len(group.members)
    return data


@router.post("/create", response_model=GroupOut, status_code=201)
def create_group(
    payload: GroupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    group = StudyGroup(name=payload.name, description=payload.description, creator_id=current_user.id)
    db.add(group)
    db.commit()
    db.refresh(group)

    # Creator automatically becomes the first member
    db.add(GroupMember(group_id=group.id, user_id=current_user.id))
    db.commit()
    db.refresh(group)
    return _serialize_group(group)


@router.get("/", response_model=list[GroupOut])
def list_groups(db: Session = Depends(get_db)):
    groups = db.query(StudyGroup).options(joinedload(StudyGroup.members)).all()
    return [_serialize_group(g) for g in groups]


@router.post("/{group_id}/join", status_code=200)
def join_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    group = db.query(StudyGroup).filter(StudyGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Study group not found")

    existing = (
        db.query(GroupMember)
        .filter(GroupMember.group_id == group_id, GroupMember.user_id == current_user.id)
        .first()
    )
    if existing:
        return {"message": "Already a member of this group"}

    db.add(GroupMember(group_id=group_id, user_id=current_user.id))
    db.commit()
    return {"message": "Joined group successfully"}


@router.post("/{group_id}/discussions", response_model=DiscussionOut, status_code=201)
def post_discussion(
    group_id: int,
    payload: DiscussionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    group = db.query(StudyGroup).filter(StudyGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Study group not found")

    is_member = (
        db.query(GroupMember)
        .filter(GroupMember.group_id == group_id, GroupMember.user_id == current_user.id)
        .first()
    )
    if not is_member:
        raise HTTPException(status_code=403, detail="Join the group before posting a discussion")

    discussion = GroupDiscussion(group_id=group_id, user_id=current_user.id, message=payload.message)
    db.add(discussion)
    db.commit()
    db.refresh(discussion)
    return discussion


@router.get("/{group_id}/discussions", response_model=list[DiscussionOut])
def get_discussions(group_id: int, db: Session = Depends(get_db)):
    discussions = (
        db.query(GroupDiscussion)
        .options(joinedload(GroupDiscussion.user))
        .filter(GroupDiscussion.group_id == group_id)
        .order_by(GroupDiscussion.created_at.asc())
        .all()
    )
    return discussions
