"""
User Model for ExamSmith Authentication System.
Defines user schema, roles, and authentication DTOs.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Literal
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User roles for authorization."""
    ADMIN = "ADMIN"
    INSTRUCTOR = "INSTRUCTOR"
    STUDENT = "STUDENT"


class UserStatus(str, Enum):
    """User account status."""
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"


# ===== Database Model =====
class User(BaseModel):
    """User document schema for MongoDB."""
    user_id: str = Field(..., description="Unique user identifier")
    email: EmailStr = Field(..., description="User email (unique)")
    password_hash: str = Field(..., description="Bcrypt hashed password")
    name: str = Field(..., description="User's full name")
    role: UserRole = Field(default=UserRole.STUDENT, description="User role")
    status: UserStatus = Field(default=UserStatus.ACTIVE, description="Account status")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    class Config:
        use_enum_values = True


# ===== Request DTOs =====
class UserCreate(BaseModel):
    """Request model for creating a new user (Admin only)."""
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=8, description="Password (min 8 chars)")
    name: str = Field(..., min_length=2, max_length=100, description="Full name")
    role: UserRole = Field(default=UserRole.STUDENT, description="User role")


class UserUpdate(BaseModel):
    """Request model for updating user (Admin only)."""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None


class LoginRequest(BaseModel):
    """Request model for user login."""
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., description="User password")


# ===== Response DTOs =====
class UserResponse(BaseModel):
    """Response model for user (excludes password)."""
    user_id: str
    email: EmailStr
    name: str
    role: UserRole
    status: UserStatus
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        use_enum_values = True


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Token expiration in seconds")


class LoginResponse(BaseModel):
    """Response model for successful login."""
    user: UserResponse
    token: TokenResponse
    message: str = "Login successful"
