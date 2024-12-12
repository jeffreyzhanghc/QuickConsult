# routers/auth.py
from fastapi import APIRouter, Depends, Response, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional
from app.core.config import settings
from app.api.v1.deps import get_db#, get_redis
from app.services.auth import AuthService
from app.schemas.auth import (
    TokenResponse,
    GoogleAuthRequest,
    UserResponse,
    ExpertResponse
)
from starlette.responses import RedirectResponse
import logging,sys


router = APIRouter()

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

@router.get("/user/google/url")
async def get_google_url(
    request: Request,
    db: Session = Depends(get_db),
    redis = None
):
    """Redirect to Google OAuth URL"""
    
    try:
        logger.info("Starting Google OAuth URL generation...")
        auth_service = AuthService(db=db)
        redirect_uri = settings.GOOGLE_REDIRECT_URI

        client = auth_service.oauth.google
        response = await client.authorize_redirect(request, redirect_uri)
        return response
    except Exception as e:
        error_msg = f"Failed to generate Google auth URL: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/user/google/callback")
async def google_callback(
    request: Request,
    db: Session = Depends(get_db),
    redis = None):
    auth_service = AuthService(db)
    #print(dict(request.query_params))
    try:
        # Exchange the authorization code for a token
        token = await auth_service.oauth.google.authorize_access_token(request)
        # Use the token to authenticate the user and create a session
        token_response = await auth_service.user_google_auth(token['id_token'])
        
        # Set cookies with the access and refresh tokens
        response = RedirectResponse(url=settings.FRONTEND_SUCCESS_REDIRECT_URL)

        response.set_cookie(
            key="access_token",
            value=token_response.access_token,
            httponly=True,
            secure=settings.SESSION_COOKIE_SECURE,  # Set to True in production with HTTPS
            samesite="lax",
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            domain=settings.COOKIE_DOMAIN,
        )
        response.set_cookie(
            key="refresh_token",
            value=token_response.refresh_token,
            httponly=True,
            secure=settings.SESSION_COOKIE_SECURE,  # Set to True in production
            samesite="lax",
            max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
            domain=settings.COOKIE_DOMAIN,
        )
        return response
    except Exception as e:
        # Redirect to an error page on the frontend
        print(e)
        return RedirectResponse(url=settings.FRONTEND_ERROR_REDIRECT_URL)


@router.get("/expert/linkedin/url")
async def get_linkedin_url(
    request: Request,
    db: Session = Depends(get_db),
    redis = None
):
   # breakpoint()
    auth_service = AuthService(db)
    redirect_uri = settings.LINKEDIN_REDIRECT_URI
    client = auth_service.oauth.linkedin
    response = await client.authorize_redirect(request, redirect_uri)
    return response  # This will redirect the user

@router.get("/expert/linkedin/callback")
async def linkedin_callback(
    request: Request,
    db: Session = Depends(get_db),
    redis = None
):
    """Handle LinkedIn OAuth callback"""
    auth_service = AuthService(db)
    try:
        # Exchange the authorization code for a token
        #print(dict(request.query_params))
        token = await auth_service.oauth.linkedin.authorize_access_token(request, client_secret=settings.SECRET_KEY)
        # Use the token to authenticate the expert and create a session
        #print("enter makesure123123")
        token_response = await auth_service.expert_linkedin_auth(token)

        # Set cookies with the access and refresh tokens
        response = RedirectResponse(url=settings.FRONTEND_SUCCESS_REDIRECT_URL)
        response.set_cookie(
            key="access_token",
            value=token_response.access_token,
            httponly=True,
            secure=settings.SESSION_COOKIE_SECURE,  # Set to True in production
            samesite="lax",
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            domain=settings.COOKIE_DOMAIN,
        )
        response.set_cookie(
            key="refresh_token",
            value=token_response.refresh_token,
            httponly=True,
            secure=settings.SESSION_COOKIE_SECURE,  # Set to True in production
            samesite="lax",
            max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
            domain=settings.COOKIE_DOMAIN,
        )
        return response
    except Exception as e:
        # Redirect to an error page on the frontend
        #print(e)
        return RedirectResponse(url=settings.FRONTEND_ERROR_REDIRECT_URL)

# Token Management Routes
@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    response: Response,
    request: Request,
    db: Session = Depends(get_db),
    redis = None
):
    """Refresh access token"""
    #breakpoint()
    refresh_token = request.cookies.get("refresh_token")
    '''
    
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No refresh token provided"
        )
    '''
    
    auth_service = AuthService(db)
    token_response = await auth_service.refresh_tokens(refresh_token)
    
    response.set_cookie(
        key="access_token",
        value=token_response.access_token,
        httponly=True,
        secure=settings.SESSION_COOKIE_SECURE,  # True in production
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        domain=settings.COOKIE_DOMAIN,
    )
    # Set new refresh token in cookie
    response.set_cookie(
        key="refresh_token",
        value=token_response.refresh_token,
        httponly=True,
        secure=settings.SESSION_COOKIE_SECURE,  # True in production
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        domain=settings.COOKIE_DOMAIN,
    )
    
    return token_response

@router.post("/logout")
async def logout(response: Response):
    """Logout user/expert"""
    # Clear access token
    response.delete_cookie(
        key="access_token",
        path="/",
        domain=settings.COOKIE_DOMAIN,
        secure=settings.SESSION_COOKIE_SECURE,
        httponly=True,
        samesite="lax"
    )
    # Clear refresh token
    response.delete_cookie(
        key="refresh_token",
        path="/",
        domain=settings.COOKIE_DOMAIN,
        secure=settings.SESSION_COOKIE_SECURE,
        httponly=True,
        samesite="lax"
    )
    return {"message": "Successfully logged out"}


@router.get("/session", response_model=Optional[UserResponse])
async def validate_session(
    request: Request,
    db: Session = Depends(get_db),
    redis = None
):
    """Validate current session"""
    # Get the access token from the cookie
   # breakpoint()
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    auth_service = AuthService(db)
    return await auth_service.validate_session(token)