# middleware/rate_limit.py
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
from redis import Redis
from app.core.config import settings

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, redis_client: Redis):
        super().__init__(app)
        self.redis = redis_client
        self.rate_limit = 100  # requests per minute for MVP
        
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host
        
        # Create Redis key
        key = f"rate_limit:{client_ip}"
        
        # Check rate limit
        requests = self.redis.get(key)
        if requests and int(requests) > self.rate_limit:
            return Response(
                status_code=429,
                content={"detail": "Too many requests"}
            )
            
        # Increment request count
        pipe = self.redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, 60)  # Reset after 1 minute
        pipe.execute()
        
        return await call_next(request)