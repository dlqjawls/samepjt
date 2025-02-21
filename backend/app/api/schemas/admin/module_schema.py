from datetime import datetime
import re
from typing import List, Optional
from pydantic import BaseModel, Field, validator
from app.api.schemas.common import Pagination, ResponseBase

class ModuleItem(BaseModel):
    module_id: int = Field(..., example=1, gt=0)
    module_nfc_tag_id: str = Field(..., example="1A1FF1043E2BC6", min_length=14, max_length=14)
    module_type_id: int = Field(..., example=2, gt=0)
    module_type_name: str = Field(..., example="medium")
    last_maintenance_at: Optional[datetime] = Field(None, example="2025-01-10T12:00:00")
    next_maintenance_at: Optional[datetime] = Field(None, example="2025-06-10T12:00:00")
    item_status_id: int = Field(..., example=1, gt=0)
    item_status_name: str = Field(..., example="active")
    created_at: datetime = Field(..., example="2024-05-01T08:30:00")
    created_by: int = Field(..., example=3)
    updated_at: datetime = Field(..., example="2025-01-10T12:00:00")
    updated_by: int = Field(..., example=5)

class ModuleData(BaseModel):
    modules: List[ModuleItem]
    pagination: Pagination

class ModuleGetResponse(ResponseBase[ModuleData]):
    class Config:
        schema_extra = {
            "example": {
                "resultCode": "SUCCESS",
                "message": "Modules retrieved successfully",
                "data": {
                    "modules": [
                        {
                            "module_id": 1,
                            "module_nfc_tag_id": "1A1FF1043E2BC6",
                            "module_type_id": 2,
                            "module_type_name": "medium",
                            "last_maintenance_at": "2025-01-10T12:00:00",
                            "next_maintenance_at": "2025-06-10T12:00:00",
                            "item_status_id": 1,
                            "item_status_name": "active",
                            "created_at": "2024-05-01T08:30:00",
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
        
class ModuleRegisterRequest(BaseModel):
    module_nfc_tag_id: str = Field(..., example="1A1FF1043E2BC6", min_length=14, max_length=14)
    module_type_id: int = Field(..., example=2, gt=0)

    @validator('module_nfc_tag_id')
    def validate_module_nfc_tag_id(cls, value: str) -> str:
        """모듈 NFC 태그 ID 형식 검증 (16진수 14자리)"""
        pattern = r'^[0-9A-F]{14}$'
        if not re.match(pattern, value):
            raise ValueError("Invalid module nfc tag id format. Must be 14 digits")
        return value

    @validator('module_type_id')
    def validate_module_type_id(cls, value: int) -> int:
        """module_type_id는 0보다 큰 값이어야 합니다."""
        if value is None or value <= 0:
            raise ValueError("module_type_id must be greater than 0")
        return value

class ModuleUpdateRequest(BaseModel):
    module_type_id: int = Field(..., example=2, gt=0)
      
class ModuleMessageResponse(ResponseBase):
    class Config:
        schema_extra = {
            "example": {
                "resultCode": "SUCCESS",
                "message": "Module {method} successfully"
            }
        }
