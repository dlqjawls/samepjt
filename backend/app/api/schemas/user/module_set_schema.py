from pydantic import BaseModel, Field
from typing import List, Optional
from app.api.schemas.common import ResponseBase, Pagination


class ModuleSetOptionType(BaseModel):
    """모듈 세트에 포함된 옵션 타입 정보"""
    optionTypeId: int = Field(..., example=1)
    optionTypeName: str = Field(..., example="배터리 팩")
    quantity: int = Field(..., example=2)


class ModuleSet(BaseModel):
    """모듈 세트 정보"""
    moduleSetId: int = Field(..., example=1)
    moduleSetName: str = Field(..., example="캠핑카 모듈 세트")
    description: Optional[str] = Field(..., example="캠핑에 최적화된 모듈 세트입니다.")
    basePrice: float = Field(..., example=2500.0)
    moduleTypeId: int = Field(..., example=3)
    moduleTypeName: str = Field(..., example="large")
    moduleTypeSize: str = Field(..., example="3x3")
    moduleTypeCost: int = Field(..., example=5000)
    imgUrls: Optional[List[str]] = Field(default=[], example=["https://example.com/module1.jpg"])

    moduleSetOptionTypes: List[ModuleSetOptionType] = Field(default=[], example=[
        {"optionTypeId": 101, "optionTypeName": "배터리 팩", "quantity": 2},
        {"optionTypeId": 102, "optionTypeName": "냉장고", "quantity": 1}
    ])


class ModuleSetData(BaseModel):
    """모듈 세트 데이터"""
    moduleSets: List[ModuleSet]
    pagination: Pagination


class ModuleSetsResponse(ResponseBase[ModuleSetData]):
    """모듈 세트 목록 조회 응답 모델"""
    class Config:
        schema_extra = {
            "example": {
                "resultCode": "SUCCESS",
                "message": "Module sets retrieved successfully",
                "data": {
                    "module_sets": [
                        {
                            "module_set_id": 1,
                            "module_set_name": "캠핑카 모듈 세트",
                            "description": "캠핑에 최적화된 모듈 세트입니다.",
                            "module_type_id": 3,
                            "module_type_name": "large",
                            "module_type_size": "3x3",
                            "module_type_cost": 5000,
                            "base_price": 12000,
                            "img_urls": ["https://example.com/module1.jpg"],
                            "module_set_option_types": [
                                {"option_type_id": 101, "option_type_name": "배터리 팩", "quantity": 2},
                                {"option_type_id": 102, "option_type_name": "냉장고", "quantity": 1}
                            ]
                        }
                    ],
                    "pagination": {
                        "currentPage": 1,
                        "totalPages": 5,
                        "totalItems": 50,
                        "pageSize": 10
                    }
                }
            }
        }
