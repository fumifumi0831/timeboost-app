from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Any
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=1)


class UserLogin(UserBase):
    password: str


class User(UserBase):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None


class UserProfileBase(BaseModel):
    interests: List[str] = Field(..., max_items=5)
    work_style: str
    rest_preferences: List[str] = Field(..., max_items=3)


class UserProfileCreate(UserProfileBase):
    pass


class UserProfileUpdate(UserProfileBase):
    pass


class UserProfile(UserProfileBase):
    id: int
    user_id: int
    textual_profile: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
