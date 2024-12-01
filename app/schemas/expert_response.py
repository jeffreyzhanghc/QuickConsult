# app/schemas/expert_response.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

class ExpertResponseBase(BaseModel):
    test_response: str
    main_response: str  # This will be encrypted before storage

class ExpertResponseCreate(ExpertResponseBase):
    pass

class ExpertResponseUpdate(BaseModel):
    test_response: Optional[str] = None
    main_response: Optional[str] = None
    status: Optional[str] = None

class ExpertResponse(ExpertResponseBase):
    id: uuid.UUID
    question_id: uuid.UUID
    expert_id: uuid.UUID
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True