from fastapi import HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.api.schemas.common import ResponseBase
from typing import Dict, Any, Optional

class BaseAPIException(HTTPException):
    """API 예외 처리의 기본 클래스"""
    def __init__(
        self, 
        status_code: int,
        error_code: str,
        message: str,
        detail: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status_code,
            detail=ResponseBase.error(
                error_code=error_code,
                message=message,
                detail=detail
            ).dict()
        )

# 400번대 에러 (클라이언트 에러)
class BadRequestError(BaseAPIException):
    """400 Bad Request"""
    def __init__(self, message: str, error_code: str = "BAD_REQUEST", detail: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=400, error_code=error_code, message=message, detail=detail)

class UnauthorizedError(BaseAPIException):
    """401 Unauthorized"""
    def __init__(self, message: str = "Authentication required", detail: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=401, error_code="UNAUTHORIZED", message=message, detail=detail)

class ForbiddenError(BaseAPIException):
    """403 Forbidden"""
    def __init__(self, message: str = "Permission denied", detail: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=403, error_code="FORBIDDEN", message=message, detail=detail)

class NotFoundError(BaseAPIException):
    """404 Not Found"""
    def __init__(self, message: str = "Resource not found", detail: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=404, error_code="NOT_FOUND", message=message, detail=detail)

class ConflictError(BaseAPIException):
    """409 Conflict"""
    def __init__(self, message: str = "Resource conflict", detail: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=409, error_code="CONFLICT", message=message, detail=detail)

class ValidationError(BaseAPIException):
    """422 Unprocessable Entity"""
    def __init__(self, message: str = "Validation error", detail: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=422, error_code="VALIDATION_ERROR", message=message, detail=detail)

# 500번대 에러 (서버 에러)
class InternalServerError(BaseAPIException):
    """500 Internal Server Error"""
    def __init__(self, message: str = "Internal server error", detail: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=500, error_code="INTERNAL_ERROR", message=message, detail=detail)

# 서비스별 커스텀 에러
class JWTError(InternalServerError):
    """JWT 시스템 에러 (500)"""
    def __init__(self, message: str = "JWT system error", detail: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            detail={"error_type": "JWT_SYSTEM_ERROR", **(detail or {})}
        )

class DatabaseError(InternalServerError):
    """데이터베이스 에러 (500)"""
    def __init__(self, message: str = "Database error", detail: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            detail={"error_type": "DATABASE_ERROR", **(detail or {})}
        )

class RedisError(InternalServerError):
    """Redis 에러 (500)"""
    def __init__(self, message: str = "Redis error", detail: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            detail={"error_type": "REDIS_ERROR", **(detail or {})}
        )

class ConfigError(InternalServerError):
    """설정 에러 (500)"""
    def __init__(self, message: str = "Configuration error", detail: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            detail={"error_type": "CONFIG_ERROR", **(detail or {})}
        )

# 전역 예외 처리기
def get_exception_handlers():
    """전역 예외 처리기들 반환"""
    async def validation_exception_handler(request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content=ResponseBase(
                resultCode="FAILURE",
                error_code="VALIDATION_ERROR",
                message="Validation error",
                detail={"errors": exc.errors()}
            ).dict()
        )

    async def http_exception_handler(request, exc: HTTPException):
        if isinstance(exc, BaseAPIException):
            return JSONResponse(status_code=exc.status_code, content=exc.detail)
            
        return JSONResponse(
            status_code=exc.status_code,
            content=ResponseBase(
                resultCode="FAILURE",
                error_code="HTTP_ERROR",
                message=str(exc.detail)
            ).dict()
        )

    return {
        RequestValidationError: validation_exception_handler,
        HTTPException: http_exception_handler
    }