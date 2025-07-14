from fastapi import FastAPI
from app.database import engine, Base
from app.schemas.schema import Base

app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "Welcome to CSEDU Backend"}
