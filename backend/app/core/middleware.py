from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, List, Callable, Any, Awaitable
from starlette.middleware.base import RequestResponseEndpoint
import time
import logging
from app.core.config import settings
from app.utils.exceptions import ConfigError
from app.api.schemas.common import ResponseBase

logger = logging.getLogger(__name__)

# 커스텀 타입 정의
MiddlewareFunction = Callable[[Request, RequestResponseEndpoint], Awaitable[Response]]
Origins = List[str]
Environment = Dict[str, Origins]

class CORSConfig:
    """CORS 설정 관리 클래스"""
    def __init__(self) -> None:
        self.environments: Environment = {
            "development": ["*"],
            "staging": [
                "https://staging.your-frontend-domain.com",
                "https://staging-api.your-domain.com"
            ],
            "production": [
                "https://your-frontend-domain.com",
                "https://api.your-domain.com"
            ]
        }

    def get_origins(self, environment: str) -> Origins:
        """환경별 CORS origins 반환"""
        if environment not in self.environments:
            raise ConfigError(
                message=f"Invalid environment: {environment}",
                detail={
                    "environment": environment,
                    "available_environments": list(self.environments.keys())
                }
            )
        return self.environments[environment]

def setup_cors_middleware(app: FastAPI) -> None:
    """CORS 미들웨어 설정"""
    try:
        cors_config = CORSConfig()
        origins = cors_config.get_origins(settings.ENVIRONMENT)

        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"]
        )
        
        logger.info(f"✅ CORS 미들웨어 설정 완료 (환경: {settings.ENVIRONMENT})")
        logger.info(f"🔹 허용된 Origins: {origins}")

    except Exception as e:
        raise ConfigError(
            message="Failed to setup CORS middleware",
            detail={"error": str(e)}
        )

async def request_logging_middleware(
    request: Request, 
    call_next: RequestResponseEndpoint
) -> Response:
    """요청/응답 로깅 미들웨어"""
    start_time = time.time()
    
    try:
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        
        log_data = {
            "path": request.url.path,
            "method": request.method,
            "status_code": response.status_code,
            "process_time_ms": round(process_time, 2)
        }
        
        if response.status_code >= 400:
            logger.error(f"Request failed: {log_data}")
        else:
            logger.info(f"Request processed: {log_data}")
            
        response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
        return response
        
    except Exception as e:
        process_time = (time.time() - start_time) * 1000
        logger.error(
            f"Request failed: {str(e)}", 
            extra={
                "path": request.url.path,
                "method": request.method,
                "process_time_ms": round(process_time, 2)
            },
            exc_info=True
        )
        return JSONResponse(
            status_code=500,
            content=ResponseBase(
                resultCode="ERROR",
                error_code="INTERNAL_SERVER_ERROR",
                message="Internal server error",
                detail={
                    "path": request.url.path,
                    "method": request.method
                }
            ).dict()
        )

def setup_middlewares(app: FastAPI) -> None:
    """미들웨어 설정"""
    try:
        setup_cors_middleware(app)
        app.middleware("http")(request_logging_middleware)
        logger.info("✅ 전체 미들웨어 설정 완료")
    except Exception as e:
        raise ConfigError(
            message="Failed to setup middlewares",
            detail={"error": str(e)}
        )