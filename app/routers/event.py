from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.oauth2 import get_current_user
from app.schemas.schema import RoleEnum, User
from app.schemas.schema import Event, EventCategory, FormData
from app.routers.fileUtils import save_upload
from datetime import date, time
from app.models.models import FormDataCreate,FormDataOut

router = APIRouter(
    prefix="/event",
    tags=["Event"]
)


@router.post("/create")
async def create_event(
    title: str = Form(...),
    date: date = Form(...),
    start_time: time = Form(...),
    end_time: time = Form(...),
    location: str = Form(...),
    description: str = Form(...),
    detailed_description: str = Form(...),
    category: EventCategory = Form(...),
    organizer: str = Form(...),
    registration_deadline: str = Form(...),
    contact_email: str = Form(...),
    max_attendees: int = Form(...),
    tags: List[str] = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != RoleEnum.admin:
        raise HTTPException(status_code=403, detail="Only admins can create events.")

    image_path = save_upload(image)

    new_event = Event(
        title=title,
        date=date,
        start_time=start_time,
        end_time=end_time,
        location=location,
        description=description,
        detailed_description=detailed_description,
        category=category,
        organizer=organizer,
        registration_deadline=registration_deadline,
        contact_email=contact_email,
        max_attendees=max_attendees,
        current_attendees=0,
        image=image_path,
        tags=tags,
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event

@router.get("/all")
def get_all_events(db: Session = Depends(get_db)):
    return db.query(Event).all()

@router.get("/{event_id}")
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found.")
    return event

@router.put("/update/{event_id}")
async def update_event(
    event_id: int,
    title: Optional[str] = Form(None),
    date: Optional[date] = Form(None),
    start_time: Optional[time] = Form(None),
    end_time: Optional[time] = Form(None),
    location: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    detailed_description: Optional[str] = Form(None),
    category: Optional[EventCategory] = Form(None),
    organizer: Optional[str] = Form(None),
    registration_deadline: Optional[str] = Form(None),
    contact_email: Optional[str] = Form(None),
    max_attendees: Optional[int] = Form(None),
    tags: Optional[List[str]] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != RoleEnum.admin:
        raise HTTPException(status_code=403, detail="Only admins can update events.")

    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found.")

    if image:
        event.image = save_upload(image)

    for field, value in locals().items():
        if field in Event.__table__.columns.keys() and value is not None:
            setattr(event, field, value)

    if tags is not None:
        event.tags = tags

    db.commit()
    db.refresh(event)
    return event

@router.delete("/delete/{event_id}")
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != RoleEnum.admin:
        raise HTTPException(status_code=403, detail="Only admins can delete events.")

    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found.")

    db.delete(event)
    db.commit()
    return {"message": "Event deleted successfully"}



@router.post("/submit", response_model=FormDataOut)
def submit_form(data: FormDataCreate, db: Session = Depends(get_db)):
    form = FormData(**data.dict())
    db.add(form)
    db.commit()
    db.refresh(form)
    return form
