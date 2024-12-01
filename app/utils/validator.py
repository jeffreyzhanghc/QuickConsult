from typing import List
import re
from fastapi import HTTPException, status

class DataValidator:
    @staticmethod
    def validate_expertise(expertise: List[str]) -> bool:
        if not expertise or len(expertise) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one expertise area is required"
            )
        
        # Validate each expertise string
        for exp in expertise:
            if not re.match(r'^[a-zA-Z0-9\s\-]+$', exp):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid expertise format: {exp}"
                )
        
        return True
    
    @staticmethod
    def validate_budget_range(min_budget: float, max_budget: float) -> bool:
        if min_budget < 0 or max_budget < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Budget cannot be negative"
            )
        
        if min_budget > max_budget:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Minimum budget cannot be greater than maximum budget"
            )
        
        return True