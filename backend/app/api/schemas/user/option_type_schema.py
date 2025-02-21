from pydantic import BaseModel, Field
from typing import List, Optional
from app.api.schemas.common import ResponseBase, Pagination

class OptionType(BaseModel):
    """옵션 타입 개별 항목 모델"""
    optionTypeId: int = Field(..., example=3)
    optionTypeName: str = Field(..., example="배터리 팩")
    optionTypeSize: str = Field(..., example="2x3x2")
    description: str = Field(..., example="캠핑 모듈용 배터리 팩")
    optionTypeCost: float = Field(..., example=100.0)
    stockQuantity: int = Field(..., example=15)
    imgUrls: List[str] = Field(default=[], example=["https://example.com/option1.jpg"])


class OptionTypesData(BaseModel):
    """옵션 타입 목록 데이터"""
    optionTypes: List[OptionType]
    pagination: Optional[Pagination] = None 


class OptionTypesResponse(ResponseBase[OptionTypesData]):
    """옵션 타입 목록 응답 모델"""
    class Config:
        schema_extra = {
            "example": {
                "resultCode": "SUCCESS",
                "message": "Option types retrieved successfully",
                "data": [
                    {
                        "optionTypeId": 1,
                        "optionTypeName": "배터리 팩",
                        "stockQuantity": 100
                    },
                    {
                        "optionTypeId": 2,
                        "optionTypeName": "냉장고",
                        "stockQuantity": 50
                    }
                ]
            }
        }
