from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
from app.api.schemas.common import ResponseBase  

class UsageHistoryItem(BaseModel):
    usage_id: int = Field(..., example=501)
    rent_id: int = Field(..., example=1)
    item_id: int = Field(..., example=101)
    item_type_name: str = Field(
        ...,
        example="vehicle",
        description="항목 유형: vehicle, module, option"
    )

    usage_status_name: str = Field(
        ...,
        example="completed",
        description="사용 상태: in_use 또는 completed"
    )
    created_at: datetime = Field(..., example="2025-01-15T08:30:00")
    updated_at: Optional[datetime] = Field(None, example="2025-01-16T12:00:00")

class Pagination(BaseModel):
    currentPage: int = Field(..., example=1)
    totalPages: int = Field(..., example=3)
    totalItems: int = Field(..., example=25)
    pageSize: int = Field(..., example=10)

class UsageHistoryData(BaseModel):
    usage_history: List[UsageHistoryItem]
    pagination: Pagination

class UsageHistoryGetResponse(ResponseBase[UsageHistoryData]):
    class Config:
        schema_extra = {
            "example": {
                "resultCode": "SUCCESS",
                "message": "사용 이력 조회 성공",
                "data": {
                  "usage_history": [
                       {
                          "usage_id": 1,
                          "rent_id": 1,
                          "item_id": 1,
                          "item_type_name": "vehicle",
                          "usage_status_name": "in_use",
                          "created_at": "2025-01-01 12:00:00",
                          "updated_at": "2025-01-01 12:00:00"
                      },
                      {
                          "usage_id": 2,
                          "rent_id": 1,
                          "item_id": 3,
                          "item_type_name": "module",
                          "usage_status_name": "in_use",
                          "created_at": "2025-01-01 12:00:00",
                          "updated_at": "2025-01-01 12:00:00"
                      } 
                  ],
                  "pagination": {
                      "currentPage": 1,
                      "totalPages": 1,
                      "totalItems": 1,
                      "pageSize": 10
                    } 
                }
            }
        } 
