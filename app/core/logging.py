# core/logging.py
import logging
from datetime import datetime
from typing import Dict, Any
import json

class APILogger:
    def __init__(self):
        self.logger = logging.getLogger("api")
        self.logger.setLevel(logging.INFO)
        
        # File handler
        fh = logging.FileHandler("api.log")
        fh.setLevel(logging.INFO)
        
        # Format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        
        self.logger.addHandler(fh)

    def log_request(self, request: Dict[str, Any]):
        """Log API request"""
        self.logger.info(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "type": "request",
            "data": request
        }))

    def log_error(self, error: Exception, context: Dict[str, Any]):
        """Log error with context"""
        self.logger.error(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "type": "error",
            "error": str(error),
            "context": context
        }))

# middleware/error_handler.py
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging import APILogger

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.logger = APILogger()
        
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
            
        except Exception as e:
            # Log error
            self.logger.log_error(e, {
                "path": request.url.path,
                "method": request.method,
                "client_ip": request.client.host
            })
            
            # Return error response
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Internal server error",
                    "error_id": datetime.utcnow().isoformat()
                }
            )