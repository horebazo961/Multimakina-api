from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=4)
    role: Optional[str] = "TECNICO"

class UserLogin(BaseModel):
    username: str
    password: str

class UserUpdateStatus(BaseModel):
    is_active: bool

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True