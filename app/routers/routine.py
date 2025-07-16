from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.oauth2 import get_current_user
from app.schemas.schema import RoomBooking, RoleEnum, RoomBookingStatus, User,Room
from app.models.models import RoomCreateInput,RoomBookingInput,UpdateRoomBookingStatusInput,Routine
from fastapi import Query
from datetime import date, time
from datetime import datetime
from sqlalchemy import and_, or_

router = APIRouter(
    prefix="/routine",
    tags=["Routine"]
)

# @router.get("/{year}/{semester}", response_model=Routine)
# def get_routine(db: Session):
#         return db.query(Routine).all()