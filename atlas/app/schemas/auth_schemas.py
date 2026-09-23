"""
Pydantic schemas for authentication endpoints
Request/response models for user authentication.
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime

from app.core.rbac import Role


# Request models
class UserLogin(BaseModel):
    """Login request"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=100)


class UserRegister(BaseModel):
    """User registration request"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: Optional[str] = Field(None, max_length=100)
    organization: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)


class TokenRefresh(BaseModel):
    """Refresh token request"""
    refresh_token: str


class PasswordChange(BaseModel):
    """Password change request"""
    old_password: str
    new_password: str = Field(..., min_length=8, max_length=100)


# Response models
class TokenResponse(BaseModel):
    """Token response after login"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class UserResponse(BaseModel):
    """User information response"""
    id: str
    username: str
    email: str
    full_name: Optional[str]
    role: Role
    is_active: bool
    is_verified: bool
    organization: Optional[str]
    department: Optional[str]
    created_at: datetime
    last_login: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str


class LoginAttemptResponse(BaseModel):
    """Login attempt information"""
    id: str
    username: str
    success: bool
    ip_address: Optional[str]
    attempted_at: datetime

    model_config = ConfigDict(from_attributes=True)
