from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None  # ← Optional ஆனது


class ChatResponse(BaseModel):
    response: str
    session_id: str
    status: str = "success"


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number")
        return v


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str