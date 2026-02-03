"""
User Schemas
Pydantic models for user authentication and management
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: str = Field(..., min_length=1, max_length=255)


class UserCreate(UserBase):
    """Schema for user registration"""
    password: str = Field(..., min_length=8, max_length=100)


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Schema for user updates"""
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=100)


class PasswordChange(BaseModel):
    """Schema for password change"""
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=100)


class UserInDB(UserBase):
    """Schema for user in database"""
    id: int
    is_active: bool
    role: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """Schema for user response (without sensitive data)"""
    id: int
    email: str
    username: str
    full_name: str
    profile_picture: Optional[str] = None
    is_active: bool
    role: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    """Schema for token payload data"""
    user_id: Optional[int] = None
    email: Optional[str] = None
