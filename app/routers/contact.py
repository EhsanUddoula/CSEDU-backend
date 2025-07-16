from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from app.database import get_db, Base
from sqlalchemy import Column, Integer, String, Text
from ..models.models import ContactMessageCreate
from ..schemas.schema import ContactMessage
router = APIRouter(
    prefix="/contact",
    tags=["contact"]
)


@router.post("")
def create_contact_message(
    contact: ContactMessageCreate,
    db: Session = Depends(get_db)
):
    db_message = ContactMessage(
        first_name=contact.firstName,
        last_name=contact.lastName,
        email=contact.email,
        subject=contact.subject,
        message=contact.message
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    # return {"message": "Contact message received!"}