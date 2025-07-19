from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models.admin_user import UserRole

class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: UserRole = UserRole.VIEWER

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    profile_pic: Optional[str] = None

class UserResponse(UserBase):
    id: int
    profile_pic: Optional[str] = None
    last_login: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse