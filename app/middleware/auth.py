# middleware/auth.py
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import time
from typing import Optional

async def auth_middleware(request: Request, call_next):
    """
    Middleware to handle timing and error handling
    Authentication is now handled by SessionMiddleware
    """
    start_time = time.time()
    
    try:
        response = await call_next(request)
        
        # Add timing header
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
        
    except Exception as exc:
        # Log error here
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"}
        )

# Helper functions for session management
async def get_session(request: Request) -> dict:
    """Get session data from request state"""
    return getattr(request.state, "session", {})

async def set_session(request: Request, key: str, value: any):
    """Set session data in request state"""
    session = await get_session(request)
    session[key] = value
    request.state.session = session