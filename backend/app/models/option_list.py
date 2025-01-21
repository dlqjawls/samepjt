from pydantic import BaseModel, Field
from typing import List, Optional
from app.models.pagination_model import Pagination


class Option(BaseModel):
    """옵션 개별 항목 모델"""
    optionId: int = Field(..., example=201)
    optionName: str = Field(..., example="배터리 팩")
    optionSize: str = Field(..., example="2x3x2")
    optionCost: float = Field(..., example=500.0)
    optionType: str = Field(..., example="switch")
    stockQuantity: int = Field(..., example=10)
    imgUrls: List[str] = Field(..., example=["https://example.com/option1.jpg"])
    description: str = Field(..., example="캠핑 모듈용 배터리 팩")


class OptionListData(BaseModel):
    """옵션 목록 데이터"""
    options: List[Option]
    pagination: Pagination


class OptionListResponse(BaseModel):
    """옵션 목록 조회 응답 모델"""
    resultCode: str = Field(..., example="SUCCESS")
    message: str = Field(..., example="Options retrieved successfully")
    data: Optional[OptionListData]
