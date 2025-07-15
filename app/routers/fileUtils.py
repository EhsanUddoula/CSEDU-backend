import os
from uuid import uuid4
from fastapi import UploadFile
from datetime import datetime
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import mimetypes

BASE_UPLOAD_PATH = "app/static/uploads"

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "pdf", "docx", "txt"}

router = APIRouter(
    prefix="",
    tags=["Files"]
)

def save_upload(file: UploadFile) -> str:
    # Ensure subdirectory exists
    upload_dir = os.path.join(BASE_UPLOAD_PATH)
    os.makedirs(upload_dir, exist_ok=True)

    # Generate unique filename
    ext = file.filename.split('.')[-1]
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    unique_filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uuid4().hex}.{ext}"

    # Full file path
    file_path = os.path.join(upload_dir, unique_filename)

    # Save file
    with open(file_path, "wb") as f:
        f.write(file.file.read())

    # Return path relative to static folder
    return f"{unique_filename}"

@router.get("/{filename}")
def get_file(filename: str):
    file_path = os.path.join("app", "static", "uploads", filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    mime_type, _ = mimetypes.guess_type(file_path)
    return FileResponse(file_path, media_type=mime_type)