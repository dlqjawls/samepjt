from pydantic import BaseModel, Field
from app.api.schemas.common import ResponseBase
from typing import Optional, List
from datetime import datetime

class MeRentInfo(BaseModel):
    """현재 로그인한 사용자의 진행중인 렌트 정보 모델"""
    rent_id: Optional[int] = Field(None, example=1)
    rentStartDate: Optional[datetime] = Field(None, example="2025-01-15T09:00:00")
    rentEndDate: Optional[datetime] = Field(None, example="2025-01-15T10:00:00")
    cost: Optional[float] = Field(None, example=100000)

class MeRentInfoResponse(ResponseBase[MeRentInfo]):
    """현재 사용자 렌트 정보 조회 응답 모델"""
    class Config:
        schema_extra = {
            "example": {
                "resultCode": "SUCCESS",
                "message": "Current rent info retrieved successfully",
                "data": {
                    "rent_id": 1,
                    "rentStartDate": "2025-01-15T09:00:00",
                    "rentEndDate": "2025-01-15T10:00:00",
                    "cost": 100000
                }
            }
        } 
        
class MeRentHistoryResponse(ResponseBase[List[MeRentInfo]]):
    """사용자 렌트 이력 조회 응답 모델"""
    class Config:
        schema_extra = {
            "example": {
                "resultCode": "SUCCESS",
                "message": "Rent history retrieved successfully",
                "data": [
                    {
                        "rent_id": 1,
                        "rentStartDate": "2025-01-15T09:00:00",
                        "rentEndDate": "2025-01-15T10:00:00",
                        "cost": 100000
                    },
                    {
                    "rent_id": 2,
                    "rentStartDate": "2025-01-15T09:00:00",
                    "rentEndDate": "2025-01-15T10:00:00",
                    "cost": 100000
                    }
                ]
            }
        }
