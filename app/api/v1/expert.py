# routers/expert.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession
from app.api.v1.deps import get_db
from app.models.user import User
from typing import List
import random

router = APIRouter(tags=["experts"])

@router.get("/test-experts")
async def get_test_experts(db: DBSession = Depends(get_db)):
    """Get two random users with expert role for testing"""
    experts = db.query(User).filter(User.role == 'expert').all()
    
    if len(experts) < 2:
        # Create some test experts if none exist
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not enough experts in database for testing. Please create some expert users first."
        )
    
    # Select 2 random experts
    test_experts = random.sample(experts, 2)
    
    # Format response
    return [
        {
            "id": str(expert.id),
            "name": expert.full_name,
            "expertise": "Test Expertise",  # You can add these fields to your User model if needed
            "rating": 4.8,
            "responseTime": "< 1 hour",
        }
        for expert in test_experts
    ]