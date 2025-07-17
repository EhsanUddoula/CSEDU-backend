from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.schemas.schema import EquipmentList, User  # adjust import paths as needed
from app.database import get_db
from app.oauth2 import get_current_user
from app.models.models import EquipmentCreate, EquipmentUpdate, EquipmentOut  # adjust import paths

router = APIRouter(prefix="/equipment", tags=["Equipment List"])

@router.post("/", response_model=EquipmentOut)
def create_equipment(
    equipment: EquipmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "Admin":
        raise HTTPException(status_code=403, detail="Only admins can add equipment.")

    new_equipment = EquipmentList(**equipment.dict())
    db.add(new_equipment)
    db.commit()
    db.refresh(new_equipment)
    return new_equipment

@router.put("/{equipment_id}", response_model=EquipmentOut)
def update_equipment(
    equipment_id: int,
    update_data: EquipmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "Admin":
        raise HTTPException(status_code=403, detail="Only admins can update equipment.")

    equipment = db.query(EquipmentList).filter_by(id=equipment_id).first()
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")

    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(equipment, key, value)

    db.commit()
    db.refresh(equipment)
    return equipment

@router.delete("/{equipment_id}")
def delete_equipment(
    equipment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "Admin":
        raise HTTPException(status_code=403, detail="Only admins can delete equipment.")

    equipment = db.query(EquipmentList).filter_by(id=equipment_id).first()
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")

    db.delete(equipment)
    db.commit()
    return {"detail": "Equipment deleted successfully"}

@router.get("/", response_model=List[EquipmentOut])
def get_all_equipment(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(EquipmentList).all()
