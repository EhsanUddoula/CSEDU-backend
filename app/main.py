from fastapi import FastAPI
from app.database import engine, Base
from app.schemas.schema import Base
from .routers import auth,routine,contact,admin,student,teacher,fileUtils,roomBook,meetings,courses,education,experience,award,publication,exam_schedule,notice,event,result
from fastapi.middleware.cors import CORSMiddleware 



app = FastAPI()

app.include_router(auth.router)
app.include_router(student.router)
app.include_router(teacher.router)
app.include_router(admin.router)
app.include_router(fileUtils.router)
app.include_router(roomBook.router)
app.include_router(meetings.router)
app.include_router(courses.router)
app.include_router(education.router)
app.include_router(experience.router)
app.include_router(award.router)
app.include_router(publication.router)
app.include_router(exam_schedule.router)
app.include_router(notice.router)
app.include_router(event.router)
app.include_router(result.router)
app.include_router(routine.router)
app.include_router(contact.router)
def configure_cors(app): 
    
    origins = [ 
        "http://localhost", 
        "https://localhost", 
        "http://localhost:5174", 
        "http://localhost:5173", 
        "http://127.0.0.1", 
    ] 
 
    app.add_middleware(  
        CORSMiddleware, 
        allow_origins=origins,  # Allows all origins or specific ones 
        allow_credentials=True, 
        allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.) 
        allow_headers=["*"],  # Allows all headers 
    ) 
     
    # Add COOP and COEP headers to the response 
    @app.middleware("http") 
    async def add_coop_coep_headers(request, call_next): 
        response = await call_next(request) 
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin" 
        response.headers["Cross-Origin-Embedder-Policy"] = "require-corp" 
        return response 
 
configure_cors(app)


# Create tables
Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "Welcome to CSEDU Backend"}
