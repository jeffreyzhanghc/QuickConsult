# app/core/deps.py
from typing import Generator, Optional
from functools import lru_cache
from fastapi import Depends, HTTPException, status, Request, status, WebSocket, WebSocketException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from redis import Redis
from jose import JWTError

from app.db.session import SessionLocal
from app.core.security import SecurityManager
from app.core.config import Settings
from app.models.user import User
from app.services.question import QuestionService
from app.services.matching import ExpertMatchingService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
settings = Settings()
security = SecurityManager(settings)

# Redis client instance
redis_client: Optional[Redis] = None

@lru_cache()
def get_settings() -> Settings:
    return Settings()

def get_security(settings: Settings = Depends(get_settings)) -> SecurityManager:
    return SecurityManager(settings)

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    except Exception as e:
        print(e)
    finally:
        db.close()
'''
def get_redis() -> Redis:
    """
    Get Redis connection.
    Initialize if not already initialized.
    """
    print("hello232566")
    global redis_client
    if redis_client is None:
        settings = get_settings()
        redis_client = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DB,
            decode_responses=True
        )
    return redis_client
'''

def get_question_service(
    db: Session = Depends(get_db),
    security: SecurityManager = Depends(get_security)
) -> QuestionService:
    return QuestionService(db, security)

def get_matching_service(
    db: Session = Depends(get_db)
) -> ExpertMatchingService:
    return ExpertMatchingService(db)


async def get_ws_current_user(
    websocket: WebSocket,
    db: Session = Depends(get_db)
) -> User:
    '''
    get user for websocket case
    '''
    # Get token from cookie in WebSocket headers
    cookies = websocket.headers.get('cookie', '')
    token = None
    
    # Parse cookies string to find access_token
    for cookie in cookies.split('; '):
        if cookie.startswith('access_token='):
            token = cookie.split('=')[1]
            break
    
    if not token:
        raise WebSocketException(code=4001)  # Authentication failed
    
    try:
        payload = security.decode_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise WebSocketException(code=4001)
        
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise WebSocketException(code=4001)
        return user
    except JWTError:
        raise WebSocketException(code=4001)
    
async def get_current_user(
    request: Request,  # Add this to get access to cookies
    db: Session = Depends(get_db)
) -> User:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    try:
        payload = security.decode_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )
        
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        return user
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

# Optional: Add role-specific user getters
async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_expert(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != "expert":
        raise HTTPException(
            status_code=403,
            detail="The user doesn't have enough privileges"
        )
    return current_user

async def get_current_client(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != "client":
        raise HTTPException(
            status_code=403,
            detail="The user doesn't have enough privileges"
        )
    return current_user