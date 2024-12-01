from pydantic import BaseModel, UUID4, Field, EmailStr
from typing import List, Optional, Dict
from datetime import datetime, time
from enum import Enum

class ExpertAvailabilityStatus(str, Enum):
    available = 'available'
    busy = 'busy'
    offline = 'offline'

class VerificationStatus(str, Enum):
    pending = 'pending'
    verified = 'verified'
    rejected = 'rejected'

class MatchStatus(str, Enum):
    pending = 'pending'
    accepted = 'accepted'
    rejected = 'rejected'
    selected = 'selected'
    expired = 'expired'

class ExpertAvailabilityCreate(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6)
    start_time: str  # HH:MM format
    end_time: str    # HH:MM format
    timezone: str

class ExpertAvailabilityResponse(ExpertAvailabilityCreate):
    id: UUID4
    expert_id: UUID4

    class Config:
        from_attributes = True

class ExpertProfileUpdate(BaseModel):
    expertise: Optional[List[str]] = None
    bio: Optional[str] = None
    hourly_rate: Optional[float] = Field(None, ge=0)
    availability_status: Optional[ExpertAvailabilityStatus] = None
    expertise_weights: Optional[Dict[str, float]] = None

class ExpertMatchResponse(BaseModel):
    id: UUID4
    sub_question_id: UUID4
    match_score: float
    status: MatchStatus
    response_deadline: datetime
    expertise_match_details: Dict[str, float]
    sub_question_details: dict  # Will include relevant question info
    created_at: datetime

    class Config:
        from_attributes = True

class ExpertDashboardStats(BaseModel):
    total_questions_answered: int
    average_rating: float
    total_earnings: float
    current_match_requests: int
    active_sessions: int

class ExpertProfileResponse(BaseModel):
    id: UUID4
    user_id: UUID4
    expertise: List[str]
    bio: Optional[str]
    hourly_rate: float
    availability_status: ExpertAvailabilityStatus
    verification_status: VerificationStatus
    background_check_status: Optional[str]
    rating: float
    total_questions: int
    expertise_weights: Dict[str, float]
    availability_schedule: List[ExpertAvailabilityResponse]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True