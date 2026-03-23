from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from uuid import UUID


class RegisterSchema(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)


class LoginSchema(BaseModel):
    email: EmailStr
    password: str


class RefreshSchema(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    roles: List[str]
    avatar: Optional[str] = None  # agar keyin qo‘shsangiz

    class Config:
        from_attributes = True


class LoginResponse(TokenResponse):
    user: UserOut