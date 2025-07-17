from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.oauth2 import get_current_user
from app.schemas.schema import Result
from app.models.models import ResultCreate, ResultUpdate, ResultOut
from app.schemas.schema import RoleEnum, User

router = APIRouter(
    prefix="/results",
    tags=["Results"]
)

@router.post("/create", response_model=ResultOut)
def create_result(
    data: ResultCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in [RoleEnum.admin, RoleEnum.teacher]:
        raise HTTPException(status_code=403, detail="Only admin or teacher can add results.")

    result = Result(**data.dict())
    db.add(result)
    db.commit()
    db.refresh(result)
    return result

@router.put("/update/{result_id}", response_model=ResultOut)
def update_result(
    result_id: int,
    data: ResultUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in [RoleEnum.admin, RoleEnum.teacher]:
        raise HTTPException(status_code=403, detail="Only admin or teacher can update results.")

    result = db.query(Result).filter(Result.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Result not found.")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(result, key, value)

    db.commit()
    db.refresh(result)
    return result

@router.get("/my", response_model=List[ResultOut])
def get_my_results(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != RoleEnum.student:
        raise HTTPException(status_code=403, detail="Only students can view their results.")

    results = db.query(Result).filter(Result.student_id == current_user.student.registration_number).all()
    return results

@router.get("/{registration_number}", response_model=List[ResultOut])
def get_results_by_registration(
    registration_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only students and teachers can access this endpoint
    if current_user.role not in [RoleEnum.student, RoleEnum.teacher]:
        raise HTTPException(status_code=403, detail="Only teachers or students can access this endpoint.")

    # If the current user is a student, they can only view their own results
    if current_user.role == RoleEnum.student and current_user.student.registration_number != registration_number:
        raise HTTPException(status_code=403, detail="You are not allowed to view another student's results.")

    results = db.query(Result).filter(Result.student_id == registration_number).all()

    if not results:
        raise HTTPException(status_code=404, detail="No results found for this registration number.")

    return results


