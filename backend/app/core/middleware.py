# app/core/middleware.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

def setup_cors_middleware(app: FastAPI) -> None:
    """환경별 CORS 미들웨어 설정"""
    origins = ["*"]  # 기본값
    
    if settings.ENVIRONMENT == "production":
        origins = [
            "https://your-frontend-domain.com",
            "https://api.your-domain.com"
        ]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )