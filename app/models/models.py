from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, Any
from datetime import date, time
from app.schemas.schema import RoomBookingStatus,MeetingStatus as MeetingStatusEnum, CourseTypeEnum

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

class CourseCreate(BaseModel):
    code: str
    title: str
    credit: int
    type: CourseTypeEnum
    year: str
    semester: str
    active: Optional[bool] = True
    content: Optional[str] = None
    degree: str
    teacher_id: Optional[int] = None

class CourseUpdateAdmin(BaseModel):
    code: Optional[str]
    title: Optional[str]
    credit: Optional[int]
    type: Optional[CourseTypeEnum]
    year: Optional[str]
    semester: Optional[str]
    active: Optional[bool]
    content: Optional[str]
    degree: Optional[str]
    teacher_id: Optional[int]=None

class CourseUpdateTeacher(BaseModel):
    content: str

