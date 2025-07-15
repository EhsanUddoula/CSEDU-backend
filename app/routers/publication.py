from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from app.schemas.schema import User,RoleEnum,Publication
from app.models.models import PublicationCreate,PublicationUpdate
from app.oauth2 import get_current_user

router = APIRouter(
    prefix="/publication",
    tags=["Teacher"]
)


@router.post("/add")
def add_publication(
    data: PublicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != RoleEnum.teacher:
        raise HTTPException(403, "Only teachers can add publications.")

    teacher = current_user.teacher
    publication = Publication(**data.dict(), teacher_id=teacher.id)
    db.add(publication)
    db.commit()
    db.refresh(publication)
    return publication


@router.get("/my")
def get_my_publications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != RoleEnum.teacher:
        raise HTTPException(403, "Only teachers can view publications.")

    teacher = current_user.teacher
    return db.query(Publication).filter(Publication.teacher_id == teacher.id).all()


@router.put("/update/{pub_id}")
def update_publication(
    pub_id: int,
    data: PublicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != RoleEnum.teacher:
        raise HTTPException(403, "Only teachers can update publications.")

    pub = db.query(Publication).filter(Publication.id == pub_id).first()
    if not pub or pub.teacher_id != current_user.teacher.id:
        raise HTTPException(404, "Publication not found or unauthorized.")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(pub, key, value)

    db.commit()
    db.refresh(pub)
    return pub


@router.delete("/delete/{pub_id}")
def delete_publication(
    pub_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != RoleEnum.teacher:
        raise HTTPException(403, "Only teachers can delete publications.")

    pub = db.query(Publication).filter(Publication.id == pub_id).first()
    if not pub or pub.teacher_id != current_user.teacher.id:
        raise HTTPException(404, "Publication not found or unauthorized.")

    db.delete(pub)
    db.commit()
    return {"message": "Publication deleted successfully."}
