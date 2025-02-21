from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, validator
from app.api.schemas.common import ResponseBase, Pagination, Coordinate
import re

class VehicleItem(BaseModel):
    """차량 개별 정보 모델"""
    vehicle_id: int = Field(..., example=1)
    vin: str = Field(..., example="ABC123456789XYZ")
    vehicle_number: str = Field(..., example="PBV-1234")
    current_location: Coordinate = Field(..., example={"x": 12.313, "y": 32.3232})
    mileage: float = Field(..., example=12000.5)
    last_maintenance_at: Optional[datetime] = Field(None, example="2025-01-10T12:00:00")
    next_maintenance_at: Optional[datetime] = Field(None, example="2025-06-10T12:00:00")
    item_status_name: str = Field(..., example="Active")
    created_at: datetime = Field(..., example="2024-05-01T08:30:00")
    created_by: int = Field(..., example=3)

    updated_at: datetime = Field(..., example="2025-01-10T12:00:00")
    updated_by: int = Field(..., example=5)

class VehiclesData(BaseModel):
    """관리자 차량 목록 및 페이지네이션 정보 모델"""
    vehicles: List[VehicleItem]
    pagination: Pagination

class VehicleGetResponse(ResponseBase[VehiclesData]):
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
                            "item_status_name": "Active",
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

class VehicleCreateRequest(BaseModel):
    """차량 등록 요청 스키마"""
    vin: str = Field(
        ...,
        description="차량의 고유한 차대번호 (Vehicle Identification Number)",
        min_length=1,
        max_length=50,
        example="ABC123456789XYZ"
    )
    vehicle_number: str = Field(
        ...,
        description="차량의 번호판",
        min_length=1,
        max_length=20,
        example="PBV-1234"
    )

    @validator('vehicle_number')
    def validate_vehicle_number(cls, v: str) -> str:
        """차량 번호 형식 검증 (PBV-숫자4자리)"""
        pattern = r'^PBV-\d{4}$'
        if not re.match(pattern, v):
            raise ValueError("Invalid vehicle number format. Must be 'PBV-' followed by 4 digits")
        return v

    @validator('vin')
    def validate_vin(cls, v: str) -> str:
        """VIN 형식 검증 (영문자와 숫자만 허용)"""
        if not v.isalnum():
            raise ValueError("VIN must contain only letters and numbers")
        return v.upper()  # VIN은 대문자로 저장

    class Config:
        schema_extra = {
            "example": {
                "vin": "ABC123456789XYZ",
                "vehicle_number": "PBV-1234"
            }
        }

class VehicleUpdateRequest(BaseModel):
    vehicle_number: Optional[str] = Field(None, example="PBV-1234")
    last_maintenance_at: Optional[datetime] = Field(None, example="2025-01-10T12:00:00")
    next_maintenance_at: Optional[datetime] = Field(None, example="2025-06-10T12:00:00")

    @validator('vehicle_number')
    def validate_vehicle_number(cls, v: str) -> str:
        """차량 번호 형식 검증 (PBV-숫자4자리)"""
        pattern = r'^PBV-\d{4}$'
        if not re.match(pattern, v):
            raise ValueError("Invalid vehicle number format. Must be 'PBV-' followed by 4 digits")
        return v

    class Config:
        schema_extra = {
            "example": {
                "vehicle_number": "PBV-5678",
                "last_maintenance_at": "2025-01-10T12:00:00",
                "next_maintenance_at": "2025-06-10T12:00:00"
            }
        }

class VehicleMessageResponse(ResponseBase):
    """관리자 차량 목록 조회 응답 모델"""
    class Config:
        schema_extra = {
            "example": {
                "resultCode": "SUCCESS",
                "message": "Vehicle {method} successfully",
            }
        }