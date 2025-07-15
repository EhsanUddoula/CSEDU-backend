from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, Any

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

