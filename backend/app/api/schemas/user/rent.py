from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class Coordinate(BaseModel):
    """SLAM 기반 좌표 정보"""
    x: float = Field(..., example=12.313)
    y: float = Field(..., example=32.3232)

class SelectedOptionType(BaseModel):
    """선택한 옵션 정보"""
    optionTypeId: int = Field(..., example=1)
    quantity: int = Field(..., example=1)

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

class RentResponse(BaseModel):
    """렌트 응답 모델"""
    rent_id: int = Field(..., example=123)
    vehicle_number: str = Field(..., example="서울 12가 3456")
