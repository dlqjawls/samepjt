from pydantic import BaseModel, Field
from typing import List, Optional
from app.api.schemas.pagination import Pagination


class moduleSetOptionType(BaseModel):
    """모듈 세트에 포함된 옵션 타입 정보"""
    optionTypeId: int = Field(..., example=1)
    optionTypeName: str = Field(..., example="배터리 팩")
    quantity: int = Field(..., example=2)


class ModuleSet(BaseModel):
    """모듈 세트 정보"""
    moduleSetId: int = Field(..., example=1)
    moduleSetName: str = Field(..., example="캠핑카 모듈 세트")
    description: str = Field(..., example="캠핑에 최적화된 모듈 세트입니다.")
    basePrice: float = Field(..., example=2500.0)
    imgsUrls: List[str] = Field(..., example=["https://example.com/module1.jpg"])
    moduleSetOptionTypes: List[moduleSetOptionType] = Field(..., example=[
        {"optionTypeId": 101, "optionTypeName": "배터리 팩", "quantity": 2},
        {"optionTypeId": 102, "optionTypeName": "냉장고", "quantity": 1}
    ])

class ModuleSetData(BaseModel):
    moduleSets: List[ModuleSet]
    pagination: Pagination

class ModuleSetsResponse(BaseModel):
    """모듈 세트 목록 조회 응답 모델"""
    resultCode: str = Field(..., example="SUCCESS")
    message: str = Field(..., example="Module sets retrieved successfully")
    data: Optional[ModuleSetData] 