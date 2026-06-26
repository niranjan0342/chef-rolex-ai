from pydantic import BaseModel

class ProfileBase(BaseModel):
    name: str
    avatar_filename: str | None = None

class ProfileCreate(ProfileBase):
    pass

class ProfileResponse(ProfileBase):
    id: int
