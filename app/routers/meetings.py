from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.oauth2 import get_current_user
from app.schemas.schema import User, RoleEnum, MeetingStatus as MeetingStatusEnum, Meeting  # reuse enum if defined in schema
from app.models.models import MeetingCreate,MeetingUpdate,MeetingOut
from fastapi import Query
from typing import Optional,List
from datetime import date, time

router = APIRouter(
    prefix="/meetings",
    tags=["Meetings"]
)

# Helper: check admin or teacher role
def is_admin_or_teacher(user: User):
    return user.role.value in ["Admin", "Teacher"]


# Create a meeting
@router.post("/", response_model=MeetingOut)
def create_meeting(
    meeting: MeetingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not is_admin_or_teacher(current_user):
        raise HTTPException(status_code=403, detail="Only admins or teachers can create meetings.")

    new_meeting = Meeting(**meeting.dict())
    db.add(new_meeting)
    db.commit()
    db.refresh(new_meeting)
    return new_meeting


# Update meeting by ID
@router.put("/{meeting_id}", response_model=MeetingOut)
def update_meeting(
    meeting_id: int,
    meeting_update: MeetingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not is_admin_or_teacher(current_user):
        raise HTTPException(status_code=403, detail="Only admins or teachers can update meetings.")

    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found.")

    update_data = meeting_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(meeting, key, value)

    db.commit()
    db.refresh(meeting)
    return meeting


# Delete meeting by ID
@router.delete("/{meeting_id}")
def delete_meeting(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not is_admin_or_teacher(current_user):
        raise HTTPException(status_code=403, detail="Only admins or teachers can delete meetings.")

    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found.")

    db.delete(meeting)
    db.commit()
    return {"message": "Meeting deleted successfully"}

@router.get("/filter", response_model=List[MeetingOut])
def filter_meetings(
    date_filter: Optional[date] = Query(None),
    time_filter: Optional[time] = Query(None),
    host_name: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    topic: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("date"),  # default sort by date
    sort_order: Optional[str] = Query("asc"),  # asc or desc
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value not in ["Admin", "Teacher"]:
        raise HTTPException(status_code=403, detail="Access denied.")

    query = db.query(Meeting)

    if date_filter:
        query = query.filter(Meeting.date == date_filter)
    if time_filter:
        query = query.filter(Meeting.time == time_filter)
    if host_name:
        query = query.filter(Meeting.host_name.ilike(f"%{host_name}%"))
    if location:
        query = query.filter(Meeting.location.ilike(f"%{location}%"))
    if topic:
        query = query.filter(Meeting.topic.ilike(f"%{topic}%"))

    # Sorting logic
    sort_column = getattr(Meeting, sort_by, None)
    if not sort_column:
        raise HTTPException(status_code=400, detail=f"Invalid sort_by field: {sort_by}")

    if sort_order.lower() == "desc":
        sort_column = sort_column.desc()
    else:
        sort_column = sort_column.asc()

    query = query.order_by(sort_column)

    results = query.all()
    return results