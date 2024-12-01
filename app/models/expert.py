from sqlalchemy import Column, ForeignKey, String, JSON, Float, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base_models import Base
import uuid
from datetime import datetime

class ExpertProfile(Base):
    __tablename__ = "expert_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    expertise = Column(JSON)  # List of expertise areas
    linkedin_id = Column(String, unique=True, nullable=True)
    bio = Column(String)
    verification_status = Column(String)  # pending, verified, rejected
    background_check_status = Column(String)  # pending, passed, failed
    hourly_rate = Column(Float)
    rating = Column(Float, default=0.0)
    total_questions = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="expert_profile")
    #responses = relationship("ExpertResponse", back_populates="expert")