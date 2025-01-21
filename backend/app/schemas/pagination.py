from typing import List, TypeVar, Generic
from pydantic import BaseModel, Field

T = TypeVar("T")


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