# services/question_service.py
from sqlalchemy import and_
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException, status
from datetime import datetime
from app.models.question import Question
from app.schemas.question import *
from app.services.ai_service import AIService

class QuestionService:
    def __init__(self, db: Session):
        self.db = db

    async def bulk_create_questions(
        self,
        client_id: UUID,
        final_content: List[str]
    ) -> List[str]:
        """Efficiently create multiple verified questions in a single transaction"""
        
        try:
            # Prepare all question objects
            questions = [
                Question(
                    client_id=client_id,
                    content=q,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                for q in final_content
            ]
            
            # Bulk insert
            #print(final_content)
            self.db.bulk_save_objects(questions)
            
            self.db.commit()
            # Return created questions
            return final_content
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save questions: {str(e)}"
            )