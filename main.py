
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware  # Import Starlette's SessionMiddleware

from app.middleware.auth import auth_middleware
from app.middleware.session import CustomSessionMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.core.config import settings
#from app.api.v1.deps import get_redis
from app.api.v1.auth import router as auth_router
from app.api.v1.question import router as question_router
from app.api.v1.session import router as session_router
from app.api.v1.expert import router as expert_router

import logging



# Configure logging


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    max_age=3600, 
    https_only = True
)

'''
if settings.REDIS_HOST:
    app.add_middleware(
        RateLimitMiddleware,
        redis_client=get_redis()
    )
'''

# Auth middleware
app.middleware("http")(auth_middleware)

# Include routers
app.include_router(
    auth_router,
    prefix=settings.API_V1_STR + "/auth",
    tags=["auth"]
)

app.include_router(
    question_router,
    prefix=settings.API_V1_STR + "/questions",
    tags=["question"]
)

app.include_router(
    session_router,
    prefix=settings.API_V1_STR + "/sessions",
    tags=["question"]
)

app.include_router(
    expert_router,
    prefix=settings.API_V1_STR + "/experts",
    tags=["question"]
)

