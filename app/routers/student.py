from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
import os
from .. import utils
from ..database import get_db
from app.schemas.schema import User,RoleEnum,Student
from app.models.models import StudentSignup
from app.oauth2 import get_current_user
from .fileUtils import save_upload

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

@router.get("/me")
def get_student_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "Student":
        raise HTTPException(status_code=403, detail="Only students can access this route.")

    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found.")

    return {
        "name": student.name,
        "father_name": student.father_name,
        "mother_name": student.mother_name,
        "session": student.session,
        "phone": student.phone,
        "hall": student.hall,
        "email": student.email,
        "address": student.address,
        "profile_pic": student.profile_pic,
        "semester": student.semester,
        "degree": student.degree,
        "registration_number": student.registration_number,
    }


@router.put("/update")
async def update_student_profile(
    father_name: str = Form(None),
    mother_name: str = Form(None),
    phone: str = Form(None),
    address: str = Form(None),
    profile_pic: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Step 1: Verify role
    if current_user.role.value != "Student":
        raise HTTPException(status_code=403, detail="Only students can update profile")

    # Step 2: Get student object
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Step 3: Update fields
    if father_name is not None:
        student.father_name = father_name
    if mother_name is not None:
        student.mother_name = mother_name
    if phone is not None:
        student.phone = phone
    if address is not None:
        student.address = address

    # Step 4: Handle profile picture upload
    if profile_pic:
        # Delete old profile pic if exists
        if student.profile_pic:
            old_path = os.path.join("app", "static", "uploads", student.profile_pic)
            if os.path.exists(old_path):
                os.remove(old_path)


        # Save new file and update path
        new_path = save_upload(profile_pic)
        student.profile_pic = new_path

    db.commit()
    return {"message": "Student profile updated successfully"}