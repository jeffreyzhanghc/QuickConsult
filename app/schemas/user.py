from pydantic import BaseModel, EmailStr, UUID4, Field
from typing import Optional, List
from datetime import datetime
import uuid

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    sub: Optional[str] = None
    exp: Optional[datetime] = None

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: str

class UserResponse(UserBase):
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    role: str

    class Config:
        from_attributes = True

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserInDBBase(UserBase):
    id: UUID4
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class User(UserInDBBase):
    pass

class UserProfile(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name: str
    role: str
    is_active: bool
    expert_profile: Optional[dict] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True




class ExpertProfileBase(BaseModel):
    expertise: List[str]
    bio: Optional[str] = None
    hourly_rate: float = Field(..., ge=0)

class ExpertProfileCreate(ExpertProfileBase):
    user_id: uuid.UUID

class ExpertProfileUpdate(ExpertProfileBase):
    pass

class ExpertProfileResponse(ExpertProfileBase):
    id: uuid.UUID
    user_id: uuid.UUID
    verification_status: str
    background_check_status: Optional[str]
    rating: Optional[float] = 0.0
    total_questions: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserWithProfile(UserResponse):
    expert_profile: Optional[ExpertProfileResponse] = None

    class Config:
        from_attributes = True
        
