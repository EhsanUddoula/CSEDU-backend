from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from app.schemas.schema import User,RoleEnum,Experience
from app.models.models import ExperienceCreate,ExperienceUpdate
from app.oauth2 import get_current_user

router = APIRouter(
    prefix="/experience",
    tags=["Teacher"]
)

@router.post("/add")
def add_experience(
    data: ExperienceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != RoleEnum.teacher:
        raise HTTPException(status_code=403, detail="Only teachers can add experience.")

    teacher = current_user.teacher
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher profile not found.")

    exp = Experience(
        title=data.title,
        organization=data.organization,
        duration=data.duration,
        year=data.year,
        teacher_id=teacher.id
    )
    db.add(exp)
    db.commit()
    db.refresh(exp)
    return exp

@router.get("/my")
def get_my_experiences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != RoleEnum.teacher:
        raise HTTPException(status_code=403, detail="Only teachers can view experience.")

    teacher = current_user.teacher
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher profile not found.")

    return db.query(Experience).filter(Experience.teacher_id == teacher.id).all()

@router.put("/update/{experience_id}")
def update_experience(
    experience_id: int,
    data: ExperienceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != RoleEnum.teacher:
        raise HTTPException(status_code=403, detail="Only teachers can update experience.")

    exp = db.query(Experience).filter(Experience.id == experience_id).first()
    if not exp or exp.teacher_id != current_user.teacher.id:
        raise HTTPException(status_code=404, detail="Experience entry not found or unauthorized.")

    update_fields = data.dict(exclude_unset=True)
    for key, value in update_fields.items():
        setattr(exp, key, value)

    db.commit()
    db.refresh(exp)
    return exp

@router.delete("/delete/{experience_id}")
def delete_experience(
    experience_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != RoleEnum.teacher:
        raise HTTPException(status_code=403, detail="Only teachers can delete experience.")

    exp = db.query(Experience).filter(Experience.id == experience_id).first()
    if not exp or exp.teacher_id != current_user.teacher.id:
        raise HTTPException(status_code=404, detail="Experience entry not found or unauthorized.")

    db.delete(exp)
    db.commit()
    return {"message": "Experience entry deleted successfully."}

