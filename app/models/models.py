from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, Any
from datetime import date, time

class AdminCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    phone: str

class StudentMetaInput(BaseModel):
    email: EmailStr
    registration_number: str
    name: str
    semester: str
    session: str
    hall: str
    degree: str

class StudentSignup(BaseModel):
    email: EmailStr
    registration_number: str
    password: str

class TeacherMetaInput(BaseModel):
    email: EmailStr
    name: str
    registration_number: str
    department: str

class TeacherSignup(BaseModel):
    email: EmailStr
    registration_number: str
    password: str

class AdminUpdate(BaseModel):
    name: str
    phone: str
    password: str

class StudentUpdate(BaseModel):
    father_name: Optional[str]
    mother_name: Optional[str]
    phone: Optional[str]
    address: Optional[str]

class RoomCreateInput(BaseModel):
    room_id: int
    location: str
    capacity: int


class RoomBookingInput(BaseModel):
    room_id: int
    date: date
    start_time: time
    end_time: time
    booking_purpose: Optional[str] = None

from app.schemas.schema import RoomBookingStatus,MeetingStatus as MeetingStatusEnum

class UpdateRoomBookingStatusInput(BaseModel):
    booking_id: int
    status: RoomBookingStatus

class MeetingCreate(BaseModel):
    date: date
    time: time
    topic: str
    host_name: str
    location: str
    status: MeetingStatusEnum = MeetingStatusEnum.pending

class MeetingUpdate(BaseModel):
    date: Optional[date]
    time: Optional[time]
    topic: Optional[str]
    host_name: Optional[str]
    location: Optional[str]
    status: Optional[MeetingStatusEnum]

class MeetingOut(BaseModel):
    id: int
    date: date
    time: time
    topic: str
    host_name: str
    location: str
    status: MeetingStatusEnum