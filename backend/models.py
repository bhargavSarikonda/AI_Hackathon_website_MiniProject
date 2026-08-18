"""
Pydantic Domain Models
Defines request and response schemas for participant registration and admin authentication.
"""

from pydantic import BaseModel, EmailStr, Field


class RegistrationCreate(BaseModel):
    """Schema for registering a student/team."""
    full_name: str = Field(..., min_length=2, max_length=100, description="Full Name of the student")
    email: EmailStr = Field(..., description="Valid student email address")
    phone: str = Field(..., min_length=10, max_length=15, description="Contact phone number")
    college: str = Field(..., min_length=2, max_length=150, description="College or University name")
    branch: str | None = Field(None, max_length=100, description="Major / Academic Branch")
    year: str | None = Field(None, max_length=20, description="Academic year (e.g. 1st Year, Final Year)")
    skills: str | None = Field(None, max_length=500, description="Technical skills and tools")
    github_url: str | None = Field(None, max_length=200, description="GitHub profile URL")
    college_id: str | None = Field(None, max_length=100, description="Student ID card number")
    team_name: str | None = Field(None, max_length=150, description="Team name")
    team_size: int | None = Field(None, ge=1, le=10, description="Team member count")
    tshirt_size: str | None = Field(None, max_length=10, description="T-shirt size (S, M, L, XL, XXL)")


class RegistrationResponse(BaseModel):
    """Schema returned after successful registration."""
    id: int
    full_name: str
    email: str
    phone: str
    college: str
    branch: str | None = None
    year: str | None = None
    skills: str | None = None
    github_url: str | None = None
    college_id: str | None = None
    team_name: str | None = None
    team_size: int | None = None
    tshirt_size: str | None = None
    created_at: str


class AdminLoginRequest(BaseModel):
    """Schema for admin login credentials."""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=4, max_length=100)


class AdminLoginResponse(BaseModel):
    """Schema returned upon successful admin login."""
    token: str
    username: str


class MessageResponse(BaseModel):
    """Generic message response schema."""
    message: str
