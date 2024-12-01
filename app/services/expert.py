# app/services/expert.py
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.expert import ExpertProfile
from app.models.question import ExpertResponse
from app.schemas.expert import ExpertProfileCreate, ExpertProfileUpdate
from app.schemas.expert_response import ExpertResponseCreate
import uuid
from datetime import datetime

class ExpertService:
    async def create_expert_profile(
        self, db: Session, profile_in: ExpertProfileCreate
    ) -> ExpertProfile:
        profile = ExpertProfile(
            id=uuid.uuid4(),
            user_id=profile_in.user_id,
            expertise=profile_in.expertise,
            bio=profile_in.bio,
            hourly_rate=profile_in.hourly_rate,
            verification_status='pending',
            background_check_status='pending'
        )
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
        return profile

    async def update_verification_status(
        self, db: Session, expert_id: uuid.UUID, status: str
    ) -> ExpertProfile:
        expert = db.query(ExpertProfile).filter(ExpertProfile.id == expert_id).first()
        if expert:
            expert.verification_status = status
            await db.commit()
            await db.refresh(expert)
        return expert

    async def get_matched_experts(
        self, db: Session, required_expertise: List[str]
    ) -> List[ExpertProfile]:
        return db.query(ExpertProfile).filter(
            ExpertProfile.verification_status == 'verified',
            ExpertProfile.expertise.overlap(required_expertise)
        ).all()
    
    async def get_expert_profile(
        self,
        db: Session,
        user_id: uuid.UUID
    ) -> Optional[ExpertProfile]:
        return db.query(ExpertProfile).filter(
            ExpertProfile.user_id == user_id
        ).first()

    async def create_expert_response(
        self,
        db: Session,
        question_id: uuid.UUID,
        expert_id: uuid.UUID,
        response_in: ExpertResponseCreate
    ) -> ExpertResponse:
        # Check if expert has already responded to this question
        existing_response = db.query(ExpertResponse).filter(
            ExpertResponse.question_id == question_id,
            ExpertResponse.expert_id == expert_id
        ).first()
        
        if existing_response:
            raise ValueError("Expert has already responded to this question")

        db_response = ExpertResponse(
            id=uuid.uuid4(),
            question_id=question_id,
            expert_id=expert_id,
            test_response=response_in.test_response,
            main_response_encrypted=response_in.main_response,
            encryption_key_encrypted="dummy_key",  # Implement actual encryption
            status="pending",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(db_response)
        await db.commit()
        await db.refresh(db_response)
        
        return db_response

    async def get_expert_responses(
        self,
        db: Session,
        expert_id: uuid.UUID
    ) -> List[ExpertResponse]:
        return db.query(ExpertResponse).filter(
            ExpertResponse.expert_id == expert_id
        ).all()

    async def get_question_responses(
        self,
        db: Session,
        question_id: uuid.UUID
    ) -> List[ExpertResponse]:
        return db.query(ExpertResponse).filter(
            ExpertResponse.question_id == question_id
        ).all()
        
    async def update_expert_profile(
        self,
        db: Session,
        expert_id: uuid.UUID,
        profile_update: ExpertProfileUpdate
    ) -> Optional[ExpertProfile]:
        expert = db.query(ExpertProfile).filter(ExpertProfile.id == expert_id).first()
        if expert:
            update_data = profile_update.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(expert, field, value)
            await db.commit()
            await db.refresh(expert)
        return expert