from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from app.api.schemas.common import ResponseBase, Pagination, Coordinate

class VehicleItem(BaseModel):
    """차량 개별 정보 모델"""
    vehicle_id: int = Field(..., example=1)
    vin: str = Field(..., example="ABC123456789XYZ")
    vehicle_number: str = Field(..., example="PBV-1234")
    current_location: Coordinate = Field(..., example={"x": 12.313, "y": 32.3232})
    mileage: float = Field(..., example=12000.5)
    last_maintenance_at: Optional[datetime] = Field(None, example="2025-01-10T12:00:00")
    next_maintenance_at: Optional[datetime] = Field(None, example="2025-06-10T12:00:00")
    status: str = Field(..., example="Active")
    created_at: datetime = Field(..., example="2024-05-01T08:30:00")
    created_by: int = Field(..., example=3)
    updated_at: datetime = Field(..., example="2025-01-10T12:00:00")
    updated_by: int = Field(..., example=5)

class VehiclesData(BaseModel):
    """관리자 차량 목록 및 페이지네이션 정보 모델"""
    vehicles: List[VehicleItem]
    pagination: Pagination

class VehiclesResponse(ResponseBase[VehiclesData]):
    """관리자 차량 목록 조회 응답 모델"""
    class Config:
        schema_extra = {
            "example": {
                "resultCode": "SUCCESS",
                "message": "Vehicle data retrieved successfully",
                "data": {
                    "vehicles": [
                        {
                            "vehicle_id": 1,
                            "vin": "ABC123456789XYZ",
                            "vehicle_number": "PBV-1234",
                            "current_location": {"x": 12.313, "y": 32.3232},
                            "mileage": 12000.5,
                            "last_maintenance_at": "2025-01-10T12:00:00",
                            "next_maintenance_at": "2025-06-10T12:00:00",
                            "status": "Active",
                            "created_at": "2024-05-01T08:30:00",
                            "created_by": 3,
                            "updated_at": "2025-01-10T12:00:00",
                            "updated_by": 5
                        }
                    ],
                    "pagination": {
                        "currentPage": 1,
                        "totalPages": 5,
                        "totalItems": 50,
                        "pageSize": 10
                    }
                }
            }
        }
