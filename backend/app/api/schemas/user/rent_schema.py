from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

from app.api.schemas.common import ResponseBase

class Coordinate(BaseModel):
    """SLAM 기반 좌표 정보"""
    x: float = Field(..., example=12.313, description="x 좌표", ge=-180, le=180)
    y: float = Field(..., example=32.3232, description="y 좌표", ge=-90, le=90)

class SelectedOptionType(BaseModel):
    """사용자가 선택한 옵션 정보"""
    optionTypeId: int = Field(..., example=1, gt=0)
    quantity: int = Field(..., example=1, gt=0)

class RentRequest(BaseModel):
    """렌트 요청 모델"""
    selectedOptionTypes: List[SelectedOptionType] = Field([], example=[
        {"optionTypeId": 1, "quantity": 1},
        {"optionTypeId": 2, "quantity": 1}
    ])
    autonomousArrivalPoint: Coordinate = Field(..., example={"x": 12.313, "y": 32.3232})
    autonomousDeparturePoint: Coordinate = Field(..., example={"x": 11.512, "y": 30.4531})
    rentStartDate: datetime = Field(..., example="2025-01-15T09:00:00")
    rentEndDate: datetime = Field(..., example="2025-01-20T18:00:00")

class RentResponseData(BaseModel):
    """렌트 응답 데이터 모델"""
    rent_id: int = Field(..., example=123)
    vehicle_number: str = Field(..., example="서울 12가 3456")

# ResponseBase를 상속받는 응답 모델들
class RentResponse(ResponseBase[RentResponseData]):
    """렌트 성공 응답 모델"""
    class Config:
        schema_extra = {
            "example": {
                "resultCode": "SUCCESS",
                "message": "Rent created successfully",
                "data": {
                    "rent_id": 123,
                    "vehicle_number": "서울 12가 3456"
                }
            }
        }
    
class CancelRentResponseData(BaseModel):
    """렌트 취소 응답 데이터 모델"""
    rent_id: int = Field(..., example=123)

class CancelRentResponse(ResponseBase[CancelRentResponseData]):
    """렌트 취소 응답 모델"""
    class Config:
        schema_extra = {
            "example": {
                "resultCode": "SUCCESS",
                "message": "Rent canceled successfully",
                "data": {
                    "rent_id": 123,
                }
            }
        }
