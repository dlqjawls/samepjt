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
        # ResponseBase.error()를 직접 사용하여 에러 응답 생성
        error_response = ResponseBase.error(
            error_code=error_code,
            message=message,
            detail=detail
        )
        super().__init__(
            status_code=status_code,
            detail=error_response.dict()
        )

# 400번대 에러 (클라이언트 에러)
class BadRequestError(BaseAPIException):
    """400 Bad Request"""
    def __init__(self, message: str, error_code: str = "BAD_REQUEST", detail: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=400, error_code=error_code, message=message, detail=detail)

class UnauthorizedError(BaseAPIException):
    """401 Unauthorized"""
    def __init__(self, message: str, error_code: str = "UNAUTHORIZED", detail: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=401, error_code=error_code, message=message, detail=detail)

class ForbiddenError(BaseAPIException):
    """403 Forbidden"""
    def __init__(self, message: str, error_code: str = "FORBIDDEN", detail: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=403, error_code=error_code, message=message, detail=detail)

class NotFoundError(BaseAPIException):
    """404 Not Found"""
    def __init__(self, message: str, error_code: str = "NOT_FOUND", detail: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=404, error_code=error_code, message=message, detail=detail)

class ConflictError(BaseAPIException):
    """409 Conflict"""
    def __init__(self, message: str, error_code: str = "CONFLICT", detail: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=409, error_code=error_code, message=message, detail=detail)

class ValidationError(BaseAPIException):
    """422 Validation Error"""
    def __init__(self, message: str, error_code: str = "VALIDATION_ERROR", detail: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=422, error_code=error_code, message=message, detail=detail)

# 500번대 에러 (서버 에러)
class InternalServerError(BaseAPIException):
    """500 Internal Server Error"""
    def __init__(self, message: str, error_code: str = "INTERNAL_SERVER_ERROR", detail: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=500, error_code=error_code, message=message, detail=detail)

class DatabaseError(InternalServerError):
    """데이터베이스 에러"""
    def __init__(self, message: str, detail: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, error_code="DATABASE_ERROR", detail=detail)

class RedisError(InternalServerError):
    """Redis 에러"""
    def __init__(self, message: str, detail: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, error_code="REDIS_ERROR", detail=detail)

class JWTError(InternalServerError):
    """JWT 에러"""
    def __init__(self, message: str, detail: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, error_code="JWT_ERROR", detail=detail)

class ConfigError(InternalServerError):
    """설정 에러"""
    def __init__(self, message: str, detail: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, error_code="CONFIG_ERROR", detail=detail)

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
            # BaseAPIException은 이미 ResponseBase.error()를 사용중
            return JSONResponse(
                status_code=exc.status_code, 
                content=exc.detail
            )
            
        # 일반 HTTPException의 경우
        return JSONResponse(
            status_code=exc.status_code,
            content=ResponseBase.error(
                error_code="HTTP_ERROR",
                message=str(exc.detail)
            ).dict()
        )

    async def global_exception_handler(request, exc: Exception):
        """예상치 못한 예외 처리"""
        return JSONResponse(
            status_code=500,
            content=ResponseBase.error(
                error_code="INTERNAL_SERVER_ERROR",
                message="Internal server error",
                detail={"error": str(exc)}
            ).dict()
        )

    return {
        RequestValidationError: validation_exception_handler,
        HTTPException: http_exception_handler,
        Exception: global_exception_handler
    }