from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from app.models.expert import ExpertProfile
from app.models.question import Question
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import uuid

class ExpertMatchingService:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
    
    async def match_experts(
        self, db: Session, question_id: uuid.UUID
    ) -> List[Dict[str, any]]:
        question = db.query(Question).filter(Question.id == question_id).first()
        experts = db.query(ExpertProfile).filter(
            ExpertProfile.verification_status == 'verified'
        ).all()
        
        # Create expertise vectors
        expert_texts = [' '.join(expert.expertise) for expert in experts]
        question_text = ' '.join(question.required_expertise)
        
        # Add question text to create combined matrix
        all_texts = expert_texts + [question_text]
        tfidf_matrix = self.vectorizer.fit_transform(all_texts)
        
        # Calculate similarities
        similarities = cosine_similarity(
            tfidf_matrix[:-1], tfidf_matrix[-1].reshape(1, -1)
        ).flatten()
        
        # Create sorted matches with scores
        matches = []
        for expert, similarity in zip(experts, similarities):
            if similarity > 0.3:  # Minimum similarity threshold
                matches.append({
                    'expert': expert,
                    'similarity_score': float(similarity),
                    'matching_expertise': self._get_matching_expertise(
                        expert.expertise,
                        question.required_expertise
                    )
                })
        
        return sorted(matches, key=lambda x: x['similarity_score'], reverse=True)
    
    def _get_matching_expertise(
        self, expert_expertise: List[str], required_expertise: List[str]
    ) -> List[str]:
        return list(set(expert_expertise) & set(required_expertise))
