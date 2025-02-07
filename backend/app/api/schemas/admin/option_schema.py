from datetime import datetime
import re
from typing import List, Optional
from pydantic import BaseModel, Field, validator
from app.api.schemas.common import Pagination, ResponseBase

class OptionItem(BaseModel):
    option_id: int = Field(..., example=101, gt=0)
    option_type_id: int = Field(..., example=1, gt=0)
    status: str = Field(..., example="active")
    last_maintenance_at: Optional[datetime] = Field(..., example="2025-01-10T12:00:00")
    next_maintenance_at: Optional[datetime] = Field(..., example="2025-06-10T12:00:00")
    created_at: datetime = Field(..., example="2024-05-01T08:30:00")
    created_by: int = Field(..., example=3)
    updated_at: datetime = Field(..., example="2025-01-10T12:00:00")
    updated_by: int = Field(..., example=5)

    class Config:
        orm_mode = True

class OptionData(BaseModel):
    options: List[OptionItem]
    pagination: Pagination

class OptionGetResponse(ResponseBase[OptionData]):
    class Config:
        schema_extra = {
            "example": {
                "resultCode": "SUCCESS",
                "message": "Options retrieved successfully",
                "data": {
                    "options": [
                        {
                          "option_id": 101,
                          "option_type_id": 1,
                          "status": "active",
                          "last_maintenance_at": "2025-01-10T12:00:00",
                          "next_maintenance_at": "2025-06-10T12:00:00",
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
        
class OptionRegisterRequest(BaseModel):
    option_type_id: int = Field(..., example=1, gt=0)
    
    @validator('option_type_id')
    def validate_option_type_id(cls, value: int) -> int:
        if value < 1:
            raise ValueError("option_type_id must be greater than 0")
        return value

class OptionRegisterResponse(ResponseBase):
    class Config:
        schema_extra = {
            "example": {
                "resultCode": "SUCCESS",
                "message": "Option registered successfully"
            }
        }

class OptionUpdateRequest(BaseModel):
    last_maintenance_at: datetime = Field(..., example="2025-01-10T12:00:00")
    next_maintenance_at: datetime = Field(..., example="2025-06-10T12:00:00")

class OptionUpdateResponse(ResponseBase):
    class Config:
        schema_extra = {
            "example": {
                "resultCode": "SUCCESS",
                "message": "Option updated successfully"
            }
        }

class OptionDeleteResponse(ResponseBase):   
    class Config:
        schema_extra = {
            "example": {
                "resultCode": "SUCCESS",
                "message": "Option deleted successfully"
            }
        }   