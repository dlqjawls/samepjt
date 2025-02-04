from typing import Generic, TypeVar, Optional, List, Dict, Any
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

T = TypeVar("T")

class ResponseBase(GenericModel, Generic[T]):
    resultCode: str = "SUCCESS"
    message: str = "Success"
    error_code: Optional[str] = None
    detail: Optional[Dict[str, Any]] = None
    data: Optional[T] = None

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def error(cls, error_code: str, message: str, detail: Optional[Dict[str, Any]] = None):
        return cls(
            resultCode="FAILURE",
            message=message,
            error_code=error_code,
            detail=detail
        )

    @classmethod
    def success(cls, data: Optional[T] = None, message: str = "Success"):
        return cls(
            resultCode="SUCCESS",
            message=message,
            data=data
        )
        
class Pagination(BaseModel):
    """📌 페이지네이션 정보 모델"""
    currentPage: int = Field(..., example=1)
    totalPages: int = Field(..., example=5)
    totalItems: int = Field(..., example=50)
    pageSize: int = Field(..., example=10)

class PaginatedResponse(BaseModel, Generic[T]):
    """📌 페이지네이션이 적용된 응답 모델"""
    items: List[T]
    pagination: Pagination 
        
class Coordinate(BaseModel):
    """SLAM 기반 좌표 정보"""
    x: float = Field(..., example=12.313, description="x 좌표", ge=-180, le=180)
    y: float = Field(..., example=32.3232, description="y 좌표", ge=-90, le=90)