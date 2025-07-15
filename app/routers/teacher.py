from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import utils
from ..database import get_db
from app.schemas.schema import User,RoleEnum,Teacher
from app.models.models import TeacherSignup
from app.oauth2 import get_current_user
from fastapi import File, Form, UploadFile
from .fileUtils import save_upload
import os

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

@router.get("/profile")
def get_teacher_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "Teacher":
        raise HTTPException(status_code=403, detail="Only teachers can view this profile")

    teacher = db.query(Teacher).filter(Teacher.user_id == current_user.id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    return {
        "name": teacher.name,
        "email": teacher.email,
        "registration_number": teacher.registration_number,
        "department": teacher.department,
        "title": teacher.title,
        "phone": teacher.phone,
        "bio": teacher.bio,
        "research_profile": teacher.research_profile,
        "profile_pic": teacher.profile_pic,
        "socials": {
            "linkedin": teacher.socials_linkedin,
            "github": teacher.socials_github,
            "twitter": teacher.socials_twitter
        }
    }



@router.put("/update")
async def update_teacher_profile(
    bio: str = Form(None),
    title: str = Form(None),
    phone: str = Form(None),
    research_profile: str = Form(None),
    linkedin: str = Form(None),
    github: str = Form(None),
    twitter: str = Form(None),
    profile_pic: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "Teacher":
        raise HTTPException(status_code=403, detail="Only teachers can update profile")

    teacher = db.query(Teacher).filter(Teacher.user_id == current_user.id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    # Update allowed fields
    if bio is not None:
        teacher.bio = bio
    if title is not None:
        teacher.title = title
    if phone is not None:
        teacher.phone = phone
    if research_profile is not None:
        teacher.research_profile = research_profile
    if linkedin is not None:
        teacher.socials_linkedin = linkedin
    if github is not None:
        teacher.socials_github = github
    if twitter is not None:
        teacher.socials_twitter = twitter

    # Handle profile picture
    if profile_pic:
        # Delete old profile pic
        if teacher.profile_pic:
            old_path = os.path.join("app", "static", "uploads", teacher.profile_pic)
            if os.path.exists(old_path):
                os.remove(old_path)

        # Save new file
        new_path = save_upload(profile_pic)
        teacher.profile_pic = new_path

    db.commit()
    return {"message": "Teacher profile updated successfully"}

@router.get("/all")
def get_all_teachers(db: Session = Depends(get_db)):
    teachers = db.query(Teacher).all()
    return [
        {
            "id": teacher.id,
            "name": teacher.name,
            "email": teacher.email,
            "title": teacher.title,
            "department": teacher.department,
            "profile_pic": teacher.profile_pic
        }
        for teacher in teachers
    ]

@router.get("/detail/{teacher_id}")
def get_teacher_detail(teacher_id: int, db: Session = Depends(get_db)):
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    return {
        "id": teacher.id,
        "name": teacher.name,
        "email": teacher.email,
        "registration_number": teacher.registration_number,
        "title": teacher.title,
        "department": teacher.department,
        "bio": teacher.bio,
        "phone": teacher.phone,
        "profile_pic": teacher.profile_pic,
        "research_profile": teacher.research_profile,
        "socials": {
            "linkedin": teacher.socials_linkedin,
            "github": teacher.socials_github,
            "twitter": teacher.socials_twitter
        },
        "education": [
            {
                "degree_name": e.degree_name,
                "major": e.major,
                "institution": e.institution,
                "year": e.year
            }
            for e in teacher.education
        ],
        "experience": [
            {
                "title": ex.title,
                "organization": ex.organization,
                "duration": ex.duration,
                "year": ex.year
            }
            for ex in teacher.experience
        ],
        "awards": [
            {
                "title": a.title,
                "type": a.type,
                "description": a.description,
                "year": a.year
            }
            for a in teacher.awards
        ],
        "publications": [
            {
                "type": p.type,
                "title": p.title,
                "url": p.url
            }
            for p in teacher.publications
        ]
    }
