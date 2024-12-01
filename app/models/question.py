# models/question.py
from sqlalchemy import Column, String, Enum, ForeignKey, JSON, Float, DateTime
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from app.models.base_models import Base, TimeStampMixin
from app.schemas.question import *
import uuid

class Question(Base, TimeStampMixin):
    __tablename__ = "questions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Self-referential relationship for breakdown questions
    client = relationship("User", back_populates="questions")
