from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from app.schemas.schema import User,RoleEnum,Education
from app.models.models import EducationCreate,EducationUpdate
from app.oauth2 import get_current_user

router = APIRouter(
    prefix="/education",
    tags=["Teacher"]
)

@router.post("/add")
def add_education(
    data: EducationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != RoleEnum.teacher:
        raise HTTPException(status_code=403, detail="Only teachers can add education.")

    teacher = current_user.teacher
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher profile not found.")

    edu = Education(
        degree_name=data.degree_name,
        major=data.major,
        institution=data.institution,
        year=data.year,
        teacher_id=teacher.id
    )
    db.add(edu)
    db.commit()
    db.refresh(edu)
    return edu

@router.post("/add")
def add_education(
    data: EducationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != RoleEnum.teacher:
        raise HTTPException(status_code=403, detail="Only teachers can add education.")

    teacher = current_user.teacher
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher profile not found.")

    edu = Education(
        degree_name=data.degree_name,
        major=data.major,
        institution=data.institution,
        year=data.year,
        teacher_id=teacher.id
    )
    db.add(edu)
    db.commit()
    db.refresh(edu)
    return edu


@router.put("/update/{education_id}")
def update_education(
    education_id: int,
    data: EducationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != RoleEnum.teacher:
        raise HTTPException(status_code=403, detail="Only teachers can update education.")

    edu = db.query(Education).filter(Education.id == education_id).first()
    if not edu or edu.teacher_id != current_user.teacher.id:
        raise HTTPException(status_code=404, detail="Education entry not found or unauthorized.")

    if data.degree_name is not None:
        edu.degree_name = data.degree_name
    if data.major is not None:
        edu.major = data.major
    if data.institution is not None:
        edu.institution = data.institution
    if data.year is not None:
        edu.year = data.year

    db.commit()
    db.refresh(edu)
    return edu

@router.get("/my")
def get_my_education(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != RoleEnum.teacher:
        raise HTTPException(status_code=403, detail="Only teachers can view education.")

    teacher = current_user.teacher
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher profile not found.")

    return db.query(Education).filter(Education.teacher_id == teacher.id).all()


@router.delete("/delete/{education_id}")
def delete_education(
    education_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != RoleEnum.teacher:
        raise HTTPException(status_code=403, detail="Only teachers can delete education.")

    edu = db.query(Education).filter(Education.id == education_id).first()
    if not edu or edu.teacher_id != current_user.teacher.id:
        raise HTTPException(status_code=404, detail="Education entry not found or unauthorized.")

    db.delete(edu)
    db.commit()
    return {"message": "Education entry deleted successfully."}

