from sqlalchemy import Boolean, Column, String, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.models.base_models import Base, TimeStampMixin

class User(Base, TimeStampMixin):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(Enum('client', 'expert', 'admin', name='user_roles'))
    is_active = Column(Boolean(), default=True)
    
    # Define relationship backref strings instead of direct class references
    expert_profile = relationship("ExpertProfile", back_populates="user", uselist=False)
    questions = relationship("Question", back_populates="client")
    notifications = relationship("Notification", back_populates="user")
    client_sessions = relationship("SessionModel", 
                                 foreign_keys="SessionModel.user_id", 
                                 back_populates="client")
    expert_sessions = relationship("SessionModel", 
                                 foreign_keys="SessionModel.expert_id", 
                                 back_populates="expert")
    sent_messages = relationship("MessageModel", back_populates="sender")