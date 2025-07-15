from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from app.schemas.schema import User,RoleEnum,Award
from app.models.models import AwardCreate,AwardUpdate
from app.oauth2 import get_current_user

router = APIRouter(
    prefix="/award",
    tags=["Teacher"]
)

@router.post("/add")
def add_award(
    data: AwardCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != RoleEnum.teacher:
        raise HTTPException(403, "Only teachers can add awards.")

    teacher = current_user.teacher
    if not teacher:
        raise HTTPException(404, "Teacher profile not found.")

    award = Award(**data.dict(), teacher_id=teacher.id)
    db.add(award)
    db.commit()
    db.refresh(award)
    return award


@router.get("/my")
def get_my_awards(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != RoleEnum.teacher:
        raise HTTPException(403, "Only teachers can view awards.")

    teacher = current_user.teacher
    return db.query(Award).filter(Award.teacher_id == teacher.id).all()


@router.put("/update/{award_id}")
def update_award(
    award_id: int,
    data: AwardUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != RoleEnum.teacher:
        raise HTTPException(403, "Only teachers can update awards.")

    award = db.query(Award).filter(Award.id == award_id).first()
    if not award or award.teacher_id != current_user.teacher.id:
        raise HTTPException(404, "Award not found or unauthorized.")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(award, key, value)

    db.commit()
    db.refresh(award)
    return award


@router.delete("/delete/{award_id}")
def delete_award(
    award_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != RoleEnum.teacher:
        raise HTTPException(403, "Only teachers can delete awards.")

    award = db.query(Award).filter(Award.id == award_id).first()
    if not award or award.teacher_id != current_user.teacher.id:
        raise HTTPException(404, "Award not found or unauthorized.")

    db.delete(award)
    db.commit()
    return {"message": "Award deleted successfully."}
