from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
from uuid import UUID

class MessageCreate(BaseModel):
    content: str

class MessageResponse(BaseModel):
    id: UUID
    content: str
    sender_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

class CreateSession(BaseModel):
    expert_id: UUID
    initial_message: str

class SessionResponse(BaseModel):
    id: UUID
    user_id: UUID
    expert_id: UUID
    status: str
    created_at: datetime
    ended_at: Optional[datetime] = None
    messages: List[MessageResponse]

    class Config:
        from_attributes = True