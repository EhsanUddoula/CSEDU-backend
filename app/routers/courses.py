from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.models import CourseCreate, CourseUpdateAdmin, CourseUpdateTeacher
from app.database import get_db
from app.oauth2 import get_current_user
from app.schemas.schema import User, RoleEnum, Course as CourseModel, CourseTypeEnum
from fastapi import Query
from typing import Optional, List
from sqlalchemy import asc, desc
from app.schemas.schema import Course

router = APIRouter(
    prefix="/course",
    tags=["Course"]
)

@router.post("/create")
def create_course(
    data: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "Admin":
        raise HTTPException(status_code=403, detail="Only admin can create courses")

    course = Course(
        code=data.code,
        title=data.title,
        credit=data.credit,
        type=data.type,
        year=data.year,
        semester=data.semester,
        content=data.content,
        degree=data.degree,
        teacher_id=data.teacher_id
    )

    db.add(course)
    db.commit()
    db.refresh(course)
    return {"message": "Course created successfully", "id": course.id}



@router.put("/update/{course_id}")
def update_course(
    course_id: int,
    admin_data: CourseUpdateAdmin = None,
    teacher_data: CourseUpdateTeacher = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    course = db.query(CourseModel).filter(CourseModel.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found.")

    if current_user.role == RoleEnum.admin:
        if not admin_data:
            raise HTTPException(status_code=400, detail="Admin update data required.")
        if admin_data.code is not None:
            course.code = admin_data.code
        if admin_data.title is not None:
            course.title = admin_data.title
        if admin_data.credit is not None:
            course.credit = admin_data.credit
        if admin_data.type is not None:
            course.type = admin_data.type
        if admin_data.year is not None:
            course.year = admin_data.year
        if admin_data.semester is not None:
            course.semester = admin_data.semester
        if admin_data.content is not None:
            course.content = admin_data.content
        if admin_data.degree is not None:
            course.degree = admin_data.degree
        if admin_data.teacher_id is not None:
            course.teacher_id = admin_data.teacher_id

        db.commit()
        db.refresh(course)
        return course

    elif current_user.role == RoleEnum.teacher:
        teacher = db.query(User).filter(User.id == current_user.id).first()
        if not teacher or not teacher.teacher or teacher.teacher.id != course.teacher_id:
            raise HTTPException(status_code=403, detail="Not authorized to update this course.")

        if not teacher_data or teacher_data.content is None:
            raise HTTPException(status_code=400, detail="Content is required for update.")

        course.content = teacher_data.content
        db.commit()
        db.refresh(course)
        return course

    else:
        raise HTTPException(status_code=403, detail="Not authorized to update course.")



@router.get("/list")
def list_courses(
    year: Optional[str] = Query(None),
    semester: Optional[str] = Query(None),
    code: Optional[str] = Query(None),
    title: Optional[str] = Query(None),
    course_type: Optional[CourseTypeEnum] = Query(None, alias="type"),
    sort_by_year: Optional[str] = Query("asc", regex="^(asc|desc)$"),
    sort_by_semester: Optional[str] = Query("asc", regex="^(asc|desc)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(CourseModel)

    # Filtering
    if year:
        query = query.filter(CourseModel.year == year)
    if semester:
        query = query.filter(CourseModel.semester == semester)
    if code:
        query = query.filter(CourseModel.code.ilike(f"%{code}%"))
    if title:
        query = query.filter(CourseModel.title.ilike(f"%{title}%"))
    if course_type:
        query = query.filter(CourseModel.type == course_type)

    # Sorting
    year_order = asc if sort_by_year == "asc" else desc
    semester_order = asc if sort_by_semester == "asc" else desc
    query = query.order_by(year_order(CourseModel.year), semester_order(CourseModel.semester))

    # Pagination
    total = query.count()
    courses = query.offset((page - 1) * page_size).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "courses": courses,
    }

@router.get("/{teacher_id}")
def get_courses_by_teacher(teacher_id: int, db: Session = Depends(get_db)):
    courses = db.query(Course).filter(Course.teacher_id == teacher_id).all()

    if not courses:
        raise HTTPException(status_code=404, detail="No courses found for this teacher")

    return courses