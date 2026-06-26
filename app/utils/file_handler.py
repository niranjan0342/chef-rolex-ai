import os
import shutil
import uuid
from fastapi import UploadFile, HTTPException

async def save_uploaded_image(file: UploadFile, destination_path: str) -> str:
    """
    Validates and saves an uploaded image.
    Returns the generated unique filename.
    """
    # Validate extension
    allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Invalid file extension. Allowed: {allowed_extensions}")
    
    # Generate unique filename to avoid overwrites
    unique_filename = f"{uuid.uuid4().hex}{ext}"
    file_location = os.path.join(destination_path, unique_filename)
    
    # Save file to disk
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
        
    return unique_filename
