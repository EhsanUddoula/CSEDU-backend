from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import utils
from ..database import get_db
from app.schemas.schema import User,RoleEnum,Student
from app.models.models import StudentSignup

router = APIRouter(
    prefix="/student",
    tags=["Student"]
)

@router.post("/signup")
def student_signup(data: StudentSignup, db: Session = Depends(get_db)):
    student = db.query(Student).filter(
        Student.email == data.email,
        Student.registration_number == data.registration_number
    ).first()

    if not student:
        raise HTTPException(404, "Student email or registration no. not pre-approved")

    if student.user_id:
        raise HTTPException(400, "This student already signed up")

    # Create User
    hashed_pw = utils.hash(data.password)
    user = User(email=data.email, password=hashed_pw, role=RoleEnum.student)
    db.add(user)
    db.commit()
    db.refresh(user)

    student.user_id = user.id
    db.commit()

    return {"message": "Student account created successfully"}
