import os
from fastapi import UploadFile
from app.utils.file_handler import save_uploaded_image

async def update_profile_picture(file: UploadFile):
    """
    Business logic for updating the profile picture.
    """
    # Define where images are stored
    storage_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "assets", "images", "profiles")
    os.makedirs(storage_path, exist_ok=True)
    
    # Save the file
    filename = await save_uploaded_image(file, storage_path)
    
    # TODO: Update the database with the new filename for the user
    
    return {
        "message": "Profile picture updated successfully",
        "filename": filename,
        "url": f"/static/assets/images/profiles/{filename}"
    }
