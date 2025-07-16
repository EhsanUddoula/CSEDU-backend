from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.schema import Notice, NoticeCategory
from app.oauth2 import get_current_user
from app.schemas.schema import RoleEnum, User
from app.routers.fileUtils import save_upload
from typing import Optional
from datetime import datetime

router = APIRouter(
    prefix="/notice",
    tags=["Notice"]
)

@router.post("/create")
def create_notice(
    title: str = Form(...),
    description: str = Form(...),
    detailed_description: str = Form(...),
    category: NoticeCategory = Form(...),
    date: str = Form(...),
    expiry_date: str = Form(...),
    author: str = Form(...),
    location: str = Form(...),
    time: str = Form(...),
    pdf_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "Admin":
        raise HTTPException(status_code=403, detail="Only admins can post notices.")

    file_path = save_upload(pdf_file) if pdf_file else None

    notice = Notice(
        title=title,
        description=description,
        detailed_description=detailed_description,
        category=category,
        date=date,
        expiry_date=expiry_date,
        author=author,
        location=location,
        time=time,
        pdf_file=file_path
    )
    db.add(notice)
    db.commit()
    return {"message": "Notice created successfully"}

@router.put("/update/{notice_id}")
def update_notice(
    notice_id: int,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    detailed_description: Optional[str] = Form(None),
    category: Optional[NoticeCategory] = Form(None),
    date: Optional[str] = Form(None),
    expiry_date: Optional[str] = Form(None),
    author: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    time: Optional[str] = Form(None),
    pdf_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "Admin":
        raise HTTPException(status_code=403, detail="Only admins can update notices.")

    notice = db.query(Notice).filter(Notice.id == notice_id).first()
    if not notice:
        raise HTTPException(status_code=404, detail="Notice not found")

    if title: notice.title = title
    if description: notice.description = description
    if detailed_description: notice.detailed_description = detailed_description
    if category: notice.category = category
    if date: notice.date = date
    if expiry_date: notice.expiry_date = expiry_date
    if author: notice.author = author
    if location: notice.location = location
    if time: notice.time = time
    if pdf_file:
        notice.pdf_file = save_upload(pdf_file)

    db.commit()
    return {"message": "Notice updated successfully"}

@router.get("/all")
def get_all_notices(db: Session = Depends(get_db)):
    return db.query(Notice).filter(Notice.is_archived == False).all()

