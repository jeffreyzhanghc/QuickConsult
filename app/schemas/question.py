# schemas/question.py
from pydantic import BaseModel, UUID4, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class QuestionStatus(str, Enum):
    pending = 'pending'          # Initial submission
    analyzing = 'analyzing'      # AI is processing
    verified = 'verified'        # User approved the breakdown/analysis
    deleted = 'deleted'          # Soft delete

class QuestionAnalyzeRequest(BaseModel):
    content: str

# Request Schemas
class QuestionCreate(BaseModel):
    content: str

class QuestionStatus(str, Enum):
    pending = 'pending'          # Initial submission
    analyzing = 'analyzing'      # AI is processing
    verified = 'verified'        # User approved the breakdown/analysis
    deleted = 'deleted'          # Soft delete

class QuestionAnalysis(BaseModel):
    original_content: str
    rephrased_versions: List[str]
    reasoning: str

class VerifyQuestionsRequest(BaseModel):
    original_content: str
    verified_questions: List[str]


class QuestionResponse(BaseModel):
    id: UUID4
    client_id: UUID4
    content: str    # The very first input from user
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
