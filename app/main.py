from fastapi import FastAPI
from app.database import engine, Base
from app.schemas.schema import Base
from .routers import auth,admin,student,teacher



app = FastAPI()

app.include_router(auth.router)
app.include_router(student.router)
app.include_router(teacher.router)
app.include_router(admin.router)


# Create tables
Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "Welcome to CSEDU Backend"}
