from datetime import datetime
import re
from typing import List, Optional
from pydantic import BaseModel, Field, validator
from app.api.schemas.common import Pagination, ResponseBase
import base64   
from fastapi import UploadFile

class ModuleSetOptionType(BaseModel):
    """모듈 세트에 포함된 옵션 타입 정보"""
    optionTypeId: int = Field(..., alias="option_type_id", example=1)
    optionTypeName: Optional[str] = Field(None, alias="option_type_name", example="배터리 팩")
    quantity: int = Field(..., example=2)

    class Config:
        allow_population_by_field_name = True

class ModuleSetItem(BaseModel):
    module_set_id: int = Field(..., example=101, gt=0)
    module_set_name: str = Field(..., example="캠핑카 모듈 세트")
    description: Optional[str] = Field(None, example="캠핑을 위한 완벽한 모듈 세트")
    module_set_images: List[str] = Field(..., example=["https://example.com/images/module-set-101.jpg", "https://example.com/images/module-set-102.jpg"])
    module_set_features: str = Field(..., example="배터리 팩, 태양광 패널 포함")
    module_type_id: int = Field(..., example=1, gt=0)
    cost: float = Field(..., example=1400)
    module_set_option_types: List[ModuleSetOptionType] = Field(..., example=[{"optionTypeId": 201, "optionTypeName": "배터리 팩", "quantity": 1}, {"optionTypeId": 202, "optionTypeName": "냉장고", "quantity": 2}])
    created_at: datetime = Field(..., example="2025-01-10T12:00:00")
    created_by: int = Field(..., example=3)
    updated_at: datetime = Field(..., example="2025-06-10T12:00:00")
    updated_by: int = Field(..., example=5)

    class Config:
        orm_mode = True

class ModuleSetData(BaseModel):
    module_sets: List[ModuleSetItem]
    pagination: Pagination

    
class ModuleSetGetResponse(ResponseBase[ModuleSetData]):
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
                            "description": "캠핑을 위한 완벽한 모듈 세트",
                            "module_set_images": [  
                              "https://example.com/images/module-set-101.jpg", 
                              "https://example.com/images/module-set-102.jpg"
                            ],
                            "module_set_features": "배터리 팩, 태양광 패널 포함",
                            "module_type_id": 1,
                            "cost": 1400,
                            "created_at": "2025-01-10T12:00:00",
                            "created_by": 3,
                            "updated_at": "2025-01-10T12:00:00",
                            "updated_by": 5
                        }
                    ],
                    "pagination": {
                        "currentPage": 1,
                        "totalPages": 3,
                        "totalItems": 25,
                        "pageSize": 10
                    }
                }
            }
        } 

class ModuleSetRegisterRequest(BaseModel):
    module_set_name: str = Field(..., example="캠핑카 모듈 세트")
    description: Optional[str] = Field(None, example="캠핑을 위한 완벽한 모듈 세트")
    module_set_images: Optional[List[UploadFile]] = Field(
        None,
        description="여러 이미지 파일을 첨부해주세요. (multipart/form-data; array of binary files)",
        example=["(binary file)", "(binary file)"]
    )
    module_set_features: Optional[str] = Field(None, example="배터리 팩, 태양광 패널")
    module_type_id: int = Field(..., example=1, gt=0, le=3)
    options: Optional[List[ModuleSetOptionType]] = Field(None, example=[{"option_type_id": 201, "quantity": 1}, {"option_type_id": 202, "quantity": 2}])    
      
class ModuleSetRegisterResponse(ResponseBase):
    class Config:
        schema_extra = {
            "example": {
                "resultCode": "SUCCESS",
                "message": "Module set registered successfully"
            }
        }

class ModuleSetUpdateRequest(BaseModel):
    module_set_name: Optional[str] = Field(None, example="캠핑카 모듈 세트")
    description: Optional[str] = Field(None, example="캠핑을 위한 완벽한 모듈 세트")
    module_set_images: Optional[List[UploadFile]] = Field(
        None,
        description="여러 이미지 파일을 첨부해주세요. (multipart/form-data; array of binary files)",
        example=["(binary file)", "(binary file)"]
    )
    module_set_features: Optional[str] = Field(None, example="배터리 팩, 태양광 패널")
    module_type_id: Optional[int] = Field(None, example=1, gt=0, le=3)
    options: Optional[List[ModuleSetOptionType]] = Field(None, example=[{"option_type_id": 201, "quantity": 1}, {"option_type_id": 202, "quantity": 2}])    
      

class ModuleSetUpdateResponse(ResponseBase):
    class Config:
        schema_extra = {
            "example": {
                "resultCode": "SUCCESS",
                "message": "Module set updated successfully"
            }
        }

class ModuleSetDeleteResponse(ResponseBase):   
    class Config:
        schema_extra = {
            "example": {
                "resultCode": "SUCCESS",
                "message": "Module set deleted successfully"
            }
        } 