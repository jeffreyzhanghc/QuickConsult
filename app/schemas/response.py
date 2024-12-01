from pydantic import BaseModel, UUID4
from typing import Optional
from datetime import datetime

class ExpertResponseBase(BaseModel):
    test_response: Optional[str] = None
    main_response: Optional[str] = None  # Will be encrypted before storage

class ExpertResponseCreate(ExpertResponseBase):
    question_id: UUID4

class ExpertResponseUpdate(ExpertResponseBase):
    status: Optional[str] = None

class ExpertResponseInDBBase(ExpertResponseBase):
    id: UUID4
    question_id: UUID4
    expert_id: UUID4
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ExpertResponse(ExpertResponseInDBBase):
    pass