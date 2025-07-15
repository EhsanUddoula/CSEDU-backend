from fastapi import APIRouter, Depends, HTTPException,Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.schema import ExamSchedule,Course, RoleEnum, User
from app.models.models import ExamScheduleCreate, ExamScheduleUpdate
from app.oauth2 import get_current_user
from sqlalchemy import and_

router = APIRouter(
    prefix="/exam",
    tags=["Exam Schedule"]
)

# Create Exam (Admin only)
@router.post("/create")
def create_exam(
    data: ExamScheduleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != RoleEnum.admin:
        raise HTTPException(403, detail="Only admin can create exams.")

    exam = ExamSchedule(**data.dict())
    db.add(exam)
    db.commit()
    db.refresh(exam)
    return exam

# Update Exam (Admin only)
@router.put("/update/{exam_id}")
def update_exam(
    exam_id: int,
    data: ExamScheduleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != RoleEnum.admin:
        raise HTTPException(403, detail="Only admin can update exams.")

    exam = db.query(ExamSchedule).filter(ExamSchedule.id == exam_id).first()
    if not exam:
        raise HTTPException(404, detail="Exam not found.")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(exam, key, value)

    db.commit()
    db.refresh(exam)
    return exam

# Delete Exam (Admin only)
@router.delete("/delete/{exam_id}")
def delete_exam(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != RoleEnum.admin:
        raise HTTPException(403, detail="Only admin can delete exams.")

    exam = db.query(ExamSchedule).filter(ExamSchedule.id == exam_id).first()
    if not exam:
        raise HTTPException(404, detail="Exam not found.")

    db.delete(exam)
    db.commit()
    return {"message": "Exam deleted successfully."}

@router.get("/filter")
def filter_exams(
    semester: str = Query(None),
    room_no: str = Query(None),
    invigilator: str = Query(None),
    course_title: str = Query(None),
    db: Session = Depends(get_db)
):
    filters = []

    if semester:
        filters.append(ExamSchedule.semester.ilike(f"%{semester}%"))
    if room_no:
        filters.append(ExamSchedule.room_no.ilike(f"%{room_no}%"))
    if invigilator:
        filters.append(ExamSchedule.invigilator.ilike(f"%{invigilator}%"))

    if course_title:
        course = db.query(Course).filter(Course.title.ilike(f"%{course_title}%")).first()
        if not course:
            return []  # No exams if course doesn't exist
        filters.append(ExamSchedule.course_id == course.id)

    exams = db.query(ExamSchedule).filter(and_(*filters)).all()
    return exams
