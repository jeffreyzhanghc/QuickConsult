from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum

class AuthType(str, Enum):
    USER = "user"
    EXPERT = "expert"

class TokenResponse(BaseModel):
    access_token: str
    refresh_token:str
    token_type: str
    user: 'UserResponse'

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: Optional[str]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ExpertResponse(BaseModel):
    id: int
    user: UserResponse
    linkedin_id: str
    expertise_areas: list[str]
    is_verified: bool
    is_available: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class GoogleAuthRequest(BaseModel):
    token: str

class LinkedInAuthRequest(BaseModel):
    code: str

TokenResponse.update_forward_refs()