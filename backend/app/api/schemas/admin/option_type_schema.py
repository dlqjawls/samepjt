from datetime import datetime
import re
from typing import List, Optional
from pydantic import BaseModel, Field, validator
from app.api.schemas.common import Pagination, ResponseBase
import base64   

class OptionTypeItem(BaseModel):
    option_type_id: int = Field(..., example=1, gt=0)
    option_type_name: str = Field(..., example="배터리 팩")
    option_type_size: str = Field(..., example="3x3")
    option_type_cost: float = Field(..., example=500.00)
    description: str = Field(..., example="중형 배터리 팩 (리튬이온)")
    option_type_images: List[str] = Field(..., example=["https://example.com/images/option-type-1.jpg"])
    option_type_features: str = Field(..., example="긴 배터리 수명, 빠른 충전")
    created_at: datetime = Field(..., example="2025-01-10T12:00:00")
    created_by: int = Field(..., example=1)
    updated_at: datetime = Field(..., example="2025-06-10T12:00:00")
    updated_by: int = Field(..., example=3)

class OptionTypeData(BaseModel):
    option_types: List[OptionTypeItem]
    pagination: Pagination
    
class OptionTypeGetResponse(ResponseBase[OptionTypeData]):
    class Config:
        schema_extra = {
            "example": {
                "resultCode": "SUCCESS",
                "message": "Option types retrieved successfully",
                "data": {
                    "option_types": [ 
                        {
                            "option_type_id": 1,
                            "option_type_name": "배터리 팩",
                            "description": "중형 배터리 팩 (리튬이온)",
                            "option_type_images": ["https://example.com/images/option-type-1.jpg"],
                            "option_type_features": "긴 배터리 수명, 빠른 충전",
                            "option_type_size": "Medium",
                            "option_type_cost": 500.00,
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

class OptionTypeRegisterRequest(BaseModel):
    option_type_name: str = Field(..., example="배터리 팩")
    option_type_size: str = Field(..., example="3x3")
    option_type_cost: float = Field(..., example=500.00)
    description: Optional[str] = Field(None, example="중형 배터리 팩 (리튬이온)")
    option_type_features: Optional[str] = Field(None, example="긴 배터리 수명, 빠른 충전")
      
class OptionTypeMessageResponse(ResponseBase):
    class Config:
        schema_extra = {
            "example": {
                "resultCode": "SUCCESS",
                "message": "Option type {method} successfully"
            }
        }

class OptionTypeUpdateRequest(BaseModel):
    option_type_name: Optional[str] = Field(None, example="배터리 팩")
    option_type_size: Optional[str] = Field(None, example="3x3")
    option_type_cost: Optional[float] = Field(None, example=500.00)
    description: Optional[str] = Field(None, example="중형 배터리 팩 (리튬이온)")
    option_type_features: Optional[str] = Field(None, example="긴 배터리 수명, 빠른 충전")

class OptionTypeRemoveImageRequest(BaseModel):
    image_url: str = Field(..., example="https://example.com/images/option-type-1.jpg", description="삭제할 이미지 URL") 
    