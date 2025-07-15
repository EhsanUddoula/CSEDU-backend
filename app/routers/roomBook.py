from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.oauth2 import get_current_user
from app.schemas.schema import RoomBooking, RoleEnum, RoomBookingStatus, User,Room
from app.models.models import RoomCreateInput,RoomBookingInput,UpdateRoomBookingStatusInput
from fastapi import Query
from datetime import date, time
from datetime import datetime
from sqlalchemy import and_, or_

router = APIRouter(
    prefix="/room",
    tags=["Room Booking"]
)

@router.post("/add")
def add_room(
    data: RoomCreateInput,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Only Admin can add rooms
    if current_user.role.value != "Admin":
        raise HTTPException(status_code=403, detail="Only admins can add new rooms.")

    # Check for unique room_id
    existing_room = db.query(Room).filter(Room.id == data.room_id).first()
    if existing_room:
        raise HTTPException(status_code=400, detail="Room with this ID already exists.")

    new_room = Room(
        id=data.room_id,
        location=data.location,
        capacity=data.capacity
    )
    db.add(new_room)
    db.commit()
    return {"message": "Room added successfully"}

@router.get("/all")
def get_all_rooms(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value not in ["Admin", "Teacher"]:
        raise HTTPException(status_code=403, detail="Access denied.")

    rooms = db.query(Room).all()
    return rooms

@router.get("/filter")
def filter_rooms(
    date_filter: date = Query(None),
    start_time_filter: time = Query(None),
    end_time_filter: time = Query(None),
    location: str = Query(None),
    min_capacity: int = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only teacher or admin can access
    if current_user.role.value not in ["Admin", "Teacher"]:
        raise HTTPException(status_code=403, detail="Access denied.")

    query = db.query(Room)

    if location:
        query = query.filter(Room.location.ilike(f"%{location}%"))
    if min_capacity:
        query = query.filter(Room.capacity >= min_capacity)

    rooms = query.all()

    # Optional: Filter rooms by booking availability
    if date_filter and (start_time_filter or end_time_filter):
        available_rooms = []
        for room in rooms:
            overlapping = db.query(RoomBooking).filter(
                RoomBooking.room_id == room.id,
                RoomBooking.date == date_filter,
                (
                    (RoomBooking.start_time <= end_time_filter) &
                    (RoomBooking.end_time >= start_time_filter)
                )
            ).first()
            if not overlapping:
                available_rooms.append(room)
        return available_rooms

    return rooms


@router.post("/book")
def book_room(
    data: RoomBookingInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Step 1: Authorization
    if current_user.role.value not in ["Admin", "Teacher"]:
        raise HTTPException(status_code=403, detail="Only teachers and admins can book rooms.")

    # Step 2: Check if room exists
    room = db.query(Room).filter(Room.id == data.room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found.")

    # Step 3: Check for time overlap on same date
    conflict = db.query(RoomBooking).filter(
        RoomBooking.room_id == data.room_id,
        RoomBooking.date == data.date,
        RoomBooking.status == "booked",
        or_(
            and_(RoomBooking.start_time <= data.start_time, RoomBooking.end_time > data.start_time),
            and_(RoomBooking.start_time < data.end_time, RoomBooking.end_time >= data.end_time),
            and_(RoomBooking.start_time >= data.start_time, RoomBooking.end_time <= data.end_time)
        )
    ).first()

    if conflict:
        raise HTTPException(status_code=409, detail="Room is already booked for this time slot.")

    # Step 4: Create the booking
    new_booking = RoomBooking(
        room_id=data.room_id,
        date=data.date,
        start_time=data.start_time,
        end_time=data.end_time,
        booking_purpose=data.booking_purpose,
        status="booked",
        user_id=current_user.id,
        booking_time=datetime.utcnow()
    )

    db.add(new_booking)
    db.commit()

    return {"message": "Room booked successfully"}

@router.put("/booking/status")
def update_booking_status(
    data: UpdateRoomBookingStatusInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "Admin":
        raise HTTPException(status_code=403, detail="Only admins can update booking status.")

    booking = db.query(RoomBooking).filter(RoomBooking.id == data.booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found.")

    booking.status = data.status
    db.commit()
    return {"message": "Booking status updated successfully"}