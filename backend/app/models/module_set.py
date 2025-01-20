from pydantic import BaseModel, Field
from typing import List, Optional


class SuppliedOption(BaseModel):
    """모듈 세트에 포함된 옵션 정보"""
    optionId: int = Field(..., example=101)
    optionName: str = Field(..., example="배터리 팩")
    quantity: int = Field(..., example=2)


class ModuleSet(BaseModel):
    """모듈 세트 정보"""
    moduleSetId: int = Field(..., example=1)
    moduleSetName: str = Field(..., example="캠핑카 모듈 세트")
    description: str = Field(..., example="캠핑에 최적화된 모듈 세트입니다.")
    totalCost: float = Field(..., example=2500.0)
    imgsUrls: List[str] = Field(..., example=["https://example.com/module1.jpg"])
    createdAt: str = Field(..., example="2024-01-20T12:00:00")
    updatedAt: str = Field(..., example="2024-01-21T14:30:00")
    suppliedOptions: List[SuppliedOption] = Field(..., example=[
        {"optionId": 101, "optionName": "배터리 팩", "quantity": 2},
        {"optionId": 102, "optionName": "냉장고", "quantity": 1}
    ])


class Pagination(BaseModel):
    """페이지네이션 정보"""
    currentPage: int = Field(..., example=1)
    totalPages: int = Field(..., example=5)
    totalItems: int = Field(..., example=50)
    pageSize: int = Field(..., example=10)

class ModuleSetData(BaseModel):
    moduleSets: List[ModuleSet]
    pagination: Pagination

class ModuleSetListResponse(BaseModel):
    """모듈 세트 목록 조회 응답 모델"""
    resultCode: str = Field(..., example="SUCCESS")
    message: str = Field(..., example="Module sets retrieved successfully")
    data: Optional[ModuleSetData] 