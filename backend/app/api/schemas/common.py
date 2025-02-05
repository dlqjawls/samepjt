from typing import Generic, TypeVar, Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from pydantic.generics import GenericModel
import json

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
    x: float = Field(..., description="X coordinate (longitude)")
    y: float = Field(..., description="Y coordinate (latitude)")

    def __str__(self) -> str:
        """좌표를 문자열로 변환"""
        return f"x={self.x},y={self.y}"


    @classmethod
    def from_str(cls, coord_str: str) -> "Coordinate":
        """문자열에서 좌표 객체 생성"""
        try:
            x, y = map(float, coord_str.split(","))
            return cls(x=x, y=y)
        except (ValueError, TypeError, AttributeError) as e:
            raise ValueError(f"Invalid coordinate string format: {coord_str}") from e