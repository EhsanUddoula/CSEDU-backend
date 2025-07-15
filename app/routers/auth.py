from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import utils
from ..oauth2 import create_access_token
from ..database import get_db
from app.schemas.schema import User

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # Get user by email (username in OAuth2PasswordRequestForm)
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Credentials (User not found)"
        )

    # Check password
    if not utils.verify(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Credentials (Password incorrect)"
        )

    # Create JWT token
    token_data = {
        "id": user.id,
        "role": user.role.value  # Extract enum value for JSON encoding
    }
    access_token = create_access_token(token_data)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }