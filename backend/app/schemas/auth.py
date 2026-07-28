from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    phone: Optional[str] = None
    college: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)

class UserResponse(UserBase):
    id: str
    is_active: bool
    is_verified: bool
    roles: List[str] = []
    
    class Config:
        from_attributes = True

class SessionResponse(BaseModel):
    id: str
    device_info: Optional[str]
    ip_address: Optional[str]
    last_active: datetime
    is_active: bool
    
    class Config:
        from_attributes = True
