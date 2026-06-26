from fastapi import APIRouter, UploadFile, File
from app.services.profile_service import update_profile_picture

router = APIRouter()

@router.post("/upload")
async def upload_profile_picture(file: UploadFile = File(...)):
    """
    Endpoint to upload and update a profile picture.
    """
    result = await update_profile_picture(file)
    return result
