from pydantic import BaseModel, EmailStr, Field


class RegistrationCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=15)
    college: str = Field(..., min_length=2, max_length=150)
    branch: str | None = Field(None, max_length=100)
    year: str | None = Field(None, max_length=20)
    skills: str | None = Field(None, max_length=500)
    github_url: str | None = Field(None, max_length=200)
    college_id: str | None = Field(None, max_length=100)
    team_name: str | None = Field(None, max_length=150)
    team_size: int | None = None
    tshirt_size: str | None = Field(None, max_length=10)


class RegistrationResponse(BaseModel):
    id: int
    full_name: str
    email: str
    phone: str
    college: str
    branch: str | None
    year: str | None
    skills: str | None
    github_url: str | None
    college_id: str | None
    team_name: str | None
    team_size: int | None
    tshirt_size: str | None
    created_at: str


class AdminLoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)


class AdminLoginResponse(BaseModel):
    token: str
    username: str


class MessageResponse(BaseModel):
    message: str
