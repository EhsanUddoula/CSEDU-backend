from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer

from .database import get_db
from app.schemas.schema import User

# ------------------- CONFIG -------------------
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ------------------- TOKEN CREATION -------------------
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ------------------- ERROR TO RAISE -------------------
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

# ------------------- VERIFY TOKEN -------------------
def verify_access_token(token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: int = payload.get("id")  # ✅ this matches your User model's `id` field
        role: str = payload.get("role")

        if id is None or role is None:
            raise credentials_exception

        user = db.query(User).filter(User.id == id).first()
        if user is None:
            raise credentials_exception

        return user
    except JWTError:
        raise credentials_exception

# ------------------- GET CURRENT USER -------------------
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    return verify_access_token(token, db)