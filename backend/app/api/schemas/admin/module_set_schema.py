from datetime import datetime
import re
from typing import List, Optional
from pydantic import BaseModel, Field, validator
from app.api.schemas.common import Pagination, ResponseBase
import base64   

class ModuleSetItem(BaseModel):
    module_set_id: int = Field(..., example=101, gt=0)
    module_set_name: str = Field(..., example="캠핑카 모듈 세트")
    description: Optional[str] = Field(None, example="캠핑을 위한 완벽한 모듈 세트")
    module_set_images: List[str] = Field(..., example=["https://example.com/images/module-set-101.jpg", "https://example.com/images/module-set-102.jpg"])
    module_set_features: str = Field(..., example="배터리 팩, 태양광 패널 포함")
    module_type_id: int = Field(..., example=1, gt=0)
    cost: float = Field(..., example=1400)
    created_at: datetime = Field(..., example="2025-01-10T12:00:00")
    created_by: int = Field(..., example=3)
    updated_at: datetime = Field(..., example="2025-06-10T12:00:00")
    updated_by: int = Field(..., example=5)

    class Config:
        orm_mode = True

class ModuleSetData(BaseModel):
    module_sets: List[ModuleSetItem]
    pagination: Pagination

class ModuleSetOptionItem(BaseModel):
    option_type_id: int = Field(..., example=200, gt=0)
    quantity: int = Field(..., example=1, gt=0)
    
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
    module_set_images: Optional[List[str]] = Field(None, example=["data:image/jpg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD...", "data:image/jpg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD..."])
    module_set_features: Optional[str] = Field(None, example="배터리 팩, 태양광 패널")
    module_type_id: int = Field(..., example=1, gt=0)
    options: Optional[List[ModuleSetOptionItem]] = Field(None, example=[{"option_type_id": 201, "quantity": 1}, {"option_type_id": 202, "quantity": 2}])    

    @validator('module_set_images')
    def validate_module_set_images(cls, value: List[str]) -> List[str]:
        """모듈 세트 이미지 형식 검증 (Base64 이미지)
        각 이미지 문자열이 'data:image/<포맷>;base64,'로 시작하며, 이후에 유효한 Base64 문자열로 디코딩이 가능한지 확인합니다.
        """
        pattern = r'^data:image\/(png|jpe?g|gif);base64,'
        if value is None:
            return value
        for img in value:
            if not re.match(pattern, img):
                raise ValueError(f"유효한 Base64 이미지 문자열 형식이 아닙니다: {img}")
            # 쉼표 뒤의 Base64 인코딩된 데이터 추출
            base64_data = img.split(',', 1)[1]
            try:
                base64.b64decode(base64_data, validate=True)
            except Exception:
                raise ValueError(f"Base64 디코딩에 실패했습니다: {img}")
        return value
      
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
    module_set_images: Optional[List[str]] = Field(None, example=["data:image/jpg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD...", "data:image/jpg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD..."])
    module_set_features: Optional[str] = Field(None, example="배터리 팩, 태양광 패널")
    module_type_id: Optional[int] = Field(None, example=1, gt=0)
    
    @validator('module_set_images')
    def validate_module_set_images(cls, value: List[str]) -> List[str]:
        """모듈 세트 이미지 형식 검증 (Base64 이미지)
        각 이미지 문자열이 'data:image/<포맷>;base64,'로 시작하며, 이후에 유효한 Base64 문자열로 디코딩이 가능한지 확인합니다.
        """
        pattern = r'^data:image\/(png|jpe?g|gif);base64,'
        if value is None:
            return value
        for img in value:
            if not re.match(pattern, img):
                raise ValueError(f"유효한 Base64 이미지 문자열 형식이 아닙니다: {img}") 
            base64_data = img.split(',', 1)[1]
            try:
                base64.b64decode(base64_data, validate=True)
            except Exception:
                raise ValueError(f"Base64 디코딩에 실패했습니다: {img}")
        return value

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