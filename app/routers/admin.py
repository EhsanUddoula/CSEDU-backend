from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import utils
from app.oauth2 import get_current_user,create_access_token
from ..database import get_db
from app.schemas.schema import User,Admin,RoleEnum,Student,Teacher
from app.models.models import AdminCreate,StudentMetaInput,TeacherMetaInput,AdminUpdate

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

@router.post("/signup")
def admin_signup(admin_data: AdminCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == admin_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = utils.hash(admin_data.password)
    user = User(email=admin_data.email, password=hashed_pw, role=RoleEnum.admin)

    db.add(user)
    db.commit()
    db.refresh(user)

    admin = Admin(user_id=user.id, email=admin_data.email, name=admin_data.name, phone=admin_data.phone, password=hashed_pw)
    db.add(admin)
    db.commit()

    # Generate JWT token
    token_data = {
        "id": user.id,
        "role": user.role.value
    }
    access_token = create_access_token(token_data)

    return {
        "message": "Admin registered successfully",
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/add/student")
def add_student_meta(
    data: StudentMetaInput,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user.role.value != "Admin":
        raise HTTPException(status_code=403, detail="Only admins can perform this action.")

    if db.query(Student).filter(Student.registration_number == data.registration_number).first():
        raise HTTPException(400, "Student already exists")

    student = Student(
        registration_number=data.registration_number,
        email=data.email,
        name=data.name,
        semester=data.semester,
        session= data.session, 
        hall= data.hall,
        degree= data.degree
    )
    db.add(student)
    db.commit()
    return {"message": "Student added. Ready to sign up."}


@router.post("/add/teacher")
def add_teacher_meta(
    data: TeacherMetaInput,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user.role.value != "Admin":
        raise HTTPException(status_code=403, detail="Only admins can perform this action.")

    if db.query(Teacher).filter(Teacher.email == data.email).first():
        raise HTTPException(status_code=400, detail="Teacher with this email already exists")

    if db.query(Teacher).filter(Teacher.registration_number == data.registration_number).first():
        raise HTTPException(status_code=400, detail="Teacher with this registration number already exists")

    teacher = Teacher(
        email=data.email,
        name=data.name,
        registration_number=data.registration_number,
        department=data.department
    )
    db.add(teacher)
    db.commit()
    return {"message": "Teacher pre-approved. Ready to sign up."}

@router.get("/me")
def get_admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "Admin":
        raise HTTPException(status_code=403, detail="Only admins can view this info.")

    admin = db.query(Admin).filter(Admin.user_id == current_user.id).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin profile not found.")

    return {
        "name": admin.name,
        "phone": admin.phone,
        "email": admin.email
    }

@router.put("/update")
def update_admin_info(
    update_data: AdminUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "Admin":
        raise HTTPException(status_code=403, detail="Only admins can update their profile.")

    admin = db.query(Admin).filter(Admin.user_id == current_user.id).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin profile not found.")

    admin.name = update_data.name
    admin.phone = update_data.phone
    admin.password = utils.hash(update_data.password)

    db.commit()
    db.refresh(admin)

    return {"message": "Admin profile updated successfully"}

@router.put("/update/student/{student_id}")
def update_student_meta(
    student_id: int,
    data: StudentMetaInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "Admin":
        raise HTTPException(status_code=403, detail="Only admins can perform this action.")

    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Check for unique registration number if changed
    if student.registration_number != data.registration_number:
        if db.query(Student).filter(Student.registration_number == data.registration_number).first():
            raise HTTPException(status_code=400, detail="Registration number already exists")

    # Update fields
    student.registration_number = data.registration_number
    student.name = data.name
    student.email = data.email
    student.semester = data.semester
    student.session = data.session
    student.hall = data.hall
    student.degree = data.degree

    db.commit()
    return {"message": "Student metadata updated successfully"}

@router.put("/update/teacher/{teacher_id}")
def update_teacher_meta(
    teacher_id: int,
    data: TeacherMetaInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "Admin":
        raise HTTPException(status_code=403, detail="Only admins can perform this action.")

    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    # Check for unique registration number if changed
    if teacher.registration_number != data.registration_number:
        if db.query(Teacher).filter(Teacher.registration_number == data.registration_number).first():
            raise HTTPException(status_code=400, detail="Registration number already exists")

    # Check for unique email if changed
    if teacher.email != data.email:
        if db.query(Teacher).filter(Teacher.email == data.email).first():
            raise HTTPException(status_code=400, detail="Email already exists")

    # Update fields
    teacher.registration_number = data.registration_number
    teacher.name = data.name
    teacher.email = data.email
    teacher.department = data.department

    db.commit()
    return {"message": "Teacher metadata updated successfully"}

