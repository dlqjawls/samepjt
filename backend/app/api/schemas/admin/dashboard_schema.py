from pydantic import BaseModel
from typing import List, Generic, TypeVar
from app.api.schemas.common import ResponseBase

T = TypeVar("T")

# 공통 응답 모델 (ResponseBase를 제네릭으로 사용)
class CountResponse(ResponseBase[int]):
    class Config:
        schema_extra = {
            "example": {
                "resultCode": "SUCCESS",
                "message": "{query} Count retrieved successfully",
                "data": 10
            }
        }

class ChartItem(BaseModel):
    state: str
    count: int
    ratio: float  # 소수점 첫째자리에서 올림한 값

class ChartListResponse(ResponseBase[List[ChartItem]]):
    class Config:
        schema_extra = {
            "example": {
                "resultCode": "SUCCESS",
                "message": "{query} state data retrieved successfully",
                "data": [
                    {"state": "inactive", "count": 20, "ratio": 33.0},
                    {"state": "active", "count": 20, "ratio": 33.0},
                    {"state": "maintenance", "count": 20, "ratio": 33.0}
                ]
            }
        }

class RentalCountItem(BaseModel):
    month: str
    count: int

class RentalCountListResponse(ResponseBase[List[RentalCountItem]]):
    class Config:
        schema_extra = {
            "example": {
                "resultCode": "SUCCESS",
                "message": "Rental counts by month retrieved successfully",
                "data": [
                    {"month": "2025-06", "count": 2},
                    {"month": "2025-07", "count": 8}
                ]
            }
        }

class MaintenanceCostItem(BaseModel):
    month: str
    cost: float

class MaintenanceCostListResponse(ResponseBase[List[MaintenanceCostItem]]):
    class Config:
        schema_extra = {
            "example": {
                "resultCode": "SUCCESS",
                "message": "Maintenance costs by month retrieved successfully",
                "data": [
                    {"month": "2025-06", "cost": 2000.0},
                    {"month": "2025-07", "cost": 1500.0}
                ]
            }
        }


class OptionPopularityItem(BaseModel):
    option_type_id: int 
    option_type_name: str
    count: int

class OptionPopularityResponse(BaseModel):
    resultCode: str
    message: str
    data: List[OptionPopularityItem]
