# services/auth.py
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from google.oauth2 import id_token
from google.auth.transport import requests
from jose import jwt
from authlib.integrations.starlette_client import OAuth

from app.core.config import settings
from app.models.user import User
from app.models.expert import ExpertProfile
from app.schemas.auth import (
    TokenResponse,
    UserResponse,
    ExpertResponse,
    AuthType
)

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self._setup_oauth()

    def _setup_oauth(self):
        """Initialize OAuth clients"""
        self.oauth = OAuth()
        
        
        # More explicit Google OAuth setup
        self.oauth.register(
            name='google',
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            authorize_state=settings.SECRET_KEY,
            server_metadata_url="https://accounts.google.com/.well-known/openid-configuration", 
            client_kwargs={
                'scope': 'profile openid email',
                'redirect_url': settings.GOOGLE_REDIRECT_URI
            }
        )
        
        # LinkedIn OAuth setup with updated configuration
        self.oauth.register(
            name='linkedin',
            client_id=settings.LINKEDIN_CLIENT_ID,
            client_secret=settings.LINKEDIN_CLIENT_SECRET,
            api_base_url='https://api.linkedin.com/v2/',
            authorize_url='https://www.linkedin.com/oauth/v2/authorization',
            access_token_url='https://www.linkedin.com/oauth/v2/accessToken',
            jwks_uri= "https://www.linkedin.com/oauth/openid/jwks",
            client_kwargs={
                'scope': 'openid profile email',
                'redirect_url': settings.LINKEDIN_REDIRECT_URI
            }
        )
        
    async def _get_or_create_user(
        self,
        email: str,
        user_data: Dict
    ) -> User:
        """Get existing user or create new one"""
        # Check if user exists
        user = self.db.query(User).filter(User.email == email).first()
        
        if not user:
            # Create new user
            user = User(
                email=email,
                full_name=user_data.get('full_name'),
                hashed_password ="testinput"
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        else:
            # Update existing user
            if user_data.get('google_id'):
                user.google_id = user_data['google_id']
            if user_data.get('full_name'):
                user.full_name = user_data['full_name']
            self.db.commit()
            self.db.refresh(user)

        return user
    
    async def user_google_auth(self, token: str) -> TokenResponse:
        """Handle Google authentication for regular users"""
        try:
            # Verify Google token
            #breakpoint()
            idinfo = id_token.verify_oauth2_token(
                token,
                requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )

            email = idinfo.get('email')
            if not email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email not provided by Google"
                )

            # Create or get user
            user = await self._get_or_create_user(
                email=email,
                user_data={
                    'full_name': idinfo.get('name'),
                    'google_id': idinfo.get('sub')
                }
            )
            user.id = str(user.id)

            # Generate tokens
            access_token, refresh_token = self._create_tokens(
                user_id=user.id,
                auth_type=AuthType.USER
            )

            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                user=UserResponse.from_orm(user)
            )

        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Google token"
            )

    async def expert_linkedin_auth(self, token: dict) -> TokenResponse:
        """Handle LinkedIn authentication for experts"""
        try:
            # Use the token to access LinkedIn APIs
            resp = await self.oauth.linkedin.get('me', token=token)
            profile = resp.json()
            
            # Get email
            email_resp = await self.oauth.linkedin.get(
                'emailAddress?q=members&projection=(elements*(handle~))', token=token
            )
            email_elements = email_resp.json().get('elements', [])
            email = email_elements[0]['handle~']['emailAddress'] if email_elements else None

            if not email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email not provided by LinkedIn"
                )

            # Create or get expert
            expert = await self._get_or_create_expert(
                email=email,
                expert_data={
                    'linkedin_id': profile.get('id'),
                    'full_name': f"{profile.get('localizedFirstName', '')} {profile.get('localizedLastName', '')}".strip()
                }
            )

            # Generate tokens
            access_token, refresh_token = self._create_tokens(
                user_id=expert.user_id,
                auth_type=AuthType.EXPERT
            )

            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                user=ExpertResponse.from_orm(expert)
            )

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"LinkedIn authentication failed: {str(e)}"
            )

    async def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        """Handle token refresh"""
        #print("enter here")
        #breakpoint()
        try:
            # Verify refresh token
            payload = jwt.decode(
                refresh_token,
                settings.REFRESH_SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )

            user_id = payload.get('sub')
            auth_type = payload.get('auth_type')

            # Generate new tokens
            access_token, new_refresh_token = self._create_tokens(
                user_id=user_id,
                auth_type=auth_type
            )

            # Get user/expert data
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            user.id = str(user.id)
            return TokenResponse(
                access_token=access_token,
                refresh_token=new_refresh_token,
                token_type="bearer",
                user=UserResponse.from_orm(user)
            )

        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )


    async def _get_or_create_expert(
        self, 
        email: str,
        expert_data: Dict
    ) -> ExpertProfile:
        """Get existing expert or create new one"""
        # First create/get user account
        user = await self._get_or_create_user(
            email=email,
            user_data={
                'full_name': expert_data.get('full_name'),
                'is_expert': True
            }
        )

        # Then get/create expert profile
        expert = self.db.query(ExpertProfile).filter(ExpertProfile.user_id == user.id).first()
        if not expert:
            expert = ExpertProfile(
                user_id=user.id,
                linkedin_id=expert_data.get('linkedin_id'),
                expertise_areas=[],  # To be filled later
                is_verified=True,    # For MVP, we trust LinkedIn
                is_available=True    # Initially available
            )
            self.db.add(expert)
            self.db.commit()
            self.db.refresh(expert)

        return expert

    def _create_tokens(
        self, 
        user_id: int,
        auth_type: AuthType
    ) -> Tuple[str, str]:
        """Create access and refresh tokens"""
        # Create access token
        access_token = jwt.encode(
            {
                "sub": str(user_id),
                "auth_type": auth_type,
                "type": "access",
                "exp": datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            },
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )

        # Create refresh token
        refresh_token = jwt.encode(
            {
                "sub": str(user_id),
                "auth_type": auth_type,
                "type": "refresh",
                "exp": datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
            },
            settings.REFRESH_SECRET_KEY,
            algorithm=settings.ALGORITHM
        )

        return access_token, refresh_token
    
    async def validate_session(self, token: str):
        """Validate access token and return user information"""
        try:
            # Decode the access token
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            user_id = payload.get('sub')
            auth_type = payload.get('auth_type')

            # Fetch the user from the database
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            user.id = str(user.id)
            return UserResponse.from_orm(user)

        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access token expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid access token"
            )