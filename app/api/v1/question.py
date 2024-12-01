# routers/questions.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.v1.deps import get_db, get_current_user
from app.schemas.question import *
from app.services.question import QuestionService
from app.services.ai_service import AIService
from app.services.matching import ExpertMatchingService
from app.schemas.user import User

import json

router = APIRouter()
@router.post("/analyze", response_model=QuestionAnalysis)
async def analyze_question(
    question: QuestionAnalyzeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Analyze the question and return suggestions.
    This doesn't save to database, just returns analysis results.
    """
    try:
        ai_service = AIService()
        
        # Get AI analysis including potential breakdowns/rephrasing
        analysis = json.loads(await ai_service.analyze_question(question.content))
        
        return QuestionAnalysis(
            original_content=question.content,
            rephrased_versions=analysis['suggested_questions'],
            reasoning=analysis['reason'],
        )
    except Exception as e:
        # Redirect to an error page on the frontend
        return

@router.post("/verify", response_model=List[str])
async def save_verified_questions(
    verified_data: VerifyQuestionsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        """Save verified questions to database efficiently"""
        question_service = QuestionService(db)
        #breakpoint()
        return await question_service.bulk_create_questions(
            client_id=current_user.id,
            final_content=verified_data.verified_questions
        )
    except Exception as e:
        # Redirect to an error page on the frontend
        return
