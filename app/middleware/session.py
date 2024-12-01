# middleware/session.py
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.security import security  # Import the security instance instead of decode_token
from itsdangerous import URLSafeSerializer
from typing import Optional, Dict
import jwt
import json

class CustomSessionMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        secret_key: str,
        session_cookie: str = "session",
        secure: bool = True,
        httponly: bool = True,
        samesite: str = "lax"
    ):
        super().__init__(app)
        self.secret_key = secret_key
        self.session_cookie = session_cookie
        self.secure = secure
        self.httponly = httponly
        self.samesite = samesite
        self.serializer = URLSafeSerializer(secret_key)
        
        # OAuth endpoints that don't require JWT auth
        self.public_endpoints = {
            "/api/v1/auth/user/google/url",
            "/api/v1/auth/user/google/callback",
            "/api/v1/auth/expert/linkedin/url",
            "/api/v1/auth/expert/linkedin/callback",
            "/api/v1/auth/refresh",
            "/api/v1/auth/logout"
        }

    async def dispatch(self, request: Request, call_next):
        # Initialize session data
        request.state.session = self.load_session(request)
        
        # Skip JWT auth for public endpoints
        if request.url.path in self.public_endpoints:
            response = await call_next(request)
            self.save_session(response, request.state.session)
            return response

        # Check JWT auth header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return Response(
                status_code=401,
                content=json.dumps({"detail": "Missing authentication"}),
                media_type="application/json"
            )

        try:
            # Validate JWT token using security instance
            token = auth_header.split(" ")[1]
            payload = security.decode_token(token)  # Use the security instance method
            
            # Add user info to request state
            request.state.user_id = payload.get("sub")
            request.state.user_type = payload.get("type")
            
            # Process request
            response = await call_next(request)
            
            # Save any session changes
            self.save_session(response, request.state.session)
            
            return response
            
        except jwt.ExpiredSignatureError:
            return Response(
                status_code=401,
                content=json.dumps({"detail": "Token has expired"}),
                media_type="application/json"
            )
        except Exception as e:
            return Response(
                status_code=401,
                content=json.dumps({"detail": "Invalid authentication"}),
                media_type="application/json"
            )

    def load_session(self, request: Request) -> Dict:
        """Load session data from cookie"""
        session_cookie = request.cookies.get(self.session_cookie)
        if not session_cookie:
            return {}
        
        try:
            return self.serializer.loads(session_cookie)
        except:
            return {}

    def save_session(self, response: Response, session_data: Dict):
        """Save session data to cookie"""
        if session_data:
            cookie_value = self.serializer.dumps(session_data)
            response.set_cookie(
                key=self.session_cookie,
                value=cookie_value,
                secure=self.secure,
                httponly=self.httponly,
                samesite=self.samesite
            )