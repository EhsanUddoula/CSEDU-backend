from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import utils
from ..database import get_db
from app.schemas.schema import User,RoleEnum,Teacher
from app.models.models import TeacherSignup

router = APIRouter(
    prefix="/teacher",
    tags=["Teacher"]
)

@router.post("/signup")
def teacher_signup(data: TeacherSignup, db: Session = Depends(get_db)):
    teacher = db.query(Teacher).filter(
        Teacher.email == data.email,
        Teacher.registration_number == data.registration_number
    ).first()

    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher email not pre-approved")

    if teacher.user_id:
        raise HTTPException(status_code=400, detail="This teacher already signed up")

    # Create user account
    hashed_pw = utils.hash(data.password)
    user = User(email=data.email, password=hashed_pw, role=RoleEnum.teacher)
    db.add(user)
    db.commit()
    db.refresh(user)

    teacher.user_id = user.id
    db.commit()

    return {"message": "Teacher account created successfully"}
