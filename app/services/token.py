# services/token.py
from datetime import datetime, timedelta
from typing import Optional
import jwt
from app.core.config import settings

class TokenService:
    def __init__(self, redis_client):
        self.redis = redis_client
        
    async def refresh_token_if_needed(self, token: str) -> Optional[str]:
        """Check if token needs refresh and handle it"""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            
            # Check if token is close to expiry (within 5 minutes)
            exp = datetime.fromtimestamp(payload["exp"])
            if datetime.utcnow() + timedelta(minutes=5) > exp:
                # Get refresh token from redis
                user_id = payload["sub"]
                refresh_token = await self.redis.get(f"refresh_token:{user_id}")
                
                if refresh_token:
                    # Use refresh token to get new access token
                    new_token = await self._refresh_access_token(refresh_token)
                    return new_token
                    
            return None
            
        except jwt.ExpiredSignatureError:
            return None
        except Exception:
            return None
            
    async def _refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """Get new access token using refresh token"""
        try:
            # Verify refresh token
            payload = jwt.decode(
                refresh_token,
                settings.REFRESH_SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            
            # Generate new access token
            access_token = self._create_access_token(
                user_id=payload["sub"],
                user_type=payload["type"]
            )
            
            return access_token
            
        except Exception:
            return None
            
    def _create_access_token(self, user_id: str, user_type: str) -> str:
        """Create new access token"""
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {
            "sub": user_id,
            "type": user_type,
            "exp": expire
        }
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)