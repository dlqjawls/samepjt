from pydantic import BaseModel, Field
from datetime import datetime
from typing import List

from app.api.schemas.common import Coordinate, ResponseBase

class SelectedOptionType(BaseModel):
    """사용자가 선택한 옵션 정보"""
    optionTypeId: int = Field(..., example=1, gt=0)
    quantity: int = Field(..., example=1, gt=0)

class RentRequest(BaseModel):
    """렌트 요청 모델"""
    selectedOptionTypes: List[SelectedOptionType] = Field(..., example=[
        {"optionTypeId": 1, "quantity": 1},
        {"optionTypeId": 2, "quantity": 1}
    ])
    autonomousArrivalPoint: Coordinate = Field(..., example={"x": 12.313, "y": 32.3232})
    autonomousDeparturePoint: Coordinate = Field(..., example={"x": 11.512, "y": 30.4531})
    moduleTypeId: int = Field(..., example=1, gt=0)
    cost: int = Field(..., example=500, gt=0)
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
        
        
class VehicleStatus(BaseModel):
    """차량 상태 정보"""
    batteryLevel: int = Field(..., ge=0, le=100)
    lightBrightness: int = Field(..., ge=0, le=100)

class OptionStatus(BaseModel):
    """옵션 상태 정보"""
    optionName: str
    optionStatus: str

class RentStatus(BaseModel):
    """렌트 상태 정보"""
    vehicle: VehicleStatus
    options: List[OptionStatus]

class RentStatusResponseData(BaseModel):
    """렌트 상태 조회 응답 데이터"""
    isArrive: bool
    location: Coordinate 
    destination: Coordinate
    ETA: datetime
    distanceTravelled: float = Field(..., ge=0)
    plannedPath: List[Coordinate]
    SLAMMapData: str
    status: RentStatus

class RentStatusResponse(ResponseBase[RentStatusResponseData]):
    """렌트 상태 조회 응답"""
    class Config:
        schema_extra = {
            "example": {
                "resultCode": "SUCCESS",
                "message": "Vehicle rent status retrieved successfully",
                "data": {
                    "isArrive": False,
                    "location": {"x": 12.313, "y": 32.3232},
                    "destination": {"x": 40.1111, "y": 100.4194},
                    "ETA": "2025-01-13T14:30:00Z",
                    "distanceTravelled": 120.0,
                    "plannedPath": [
                        {"x": 12.3200, "y": 32.3300},
                        {"x": 15.4500, "y": 35.6000}
                    ],
                    "SLAMMapData": "base64-encoded-map-data",
                    "status": {
                        "vehicle": {
                            "batteryLevel": 85,
                            "lightBrightness": 80
                        },
                        "options": [
                            {
                                "optionName": "물탱크",
                                "optionStatus": "잔여량: 50L"
                            },
                            {
                                "optionName": "배터리 팩",
                                "optionStatus": "잔여량: 80%"
                            }
                        ]
                    }
                }
            }
        }

class CompleteRentResponseData(BaseModel):
    """렌트 완료 응답 데이터 모델"""
    rent_id: int = Field(..., example=123)
    total_mileage: float = Field(..., example=150.0)
    usage_duration: int = Field(..., example=3)
    estimated_payback_amount: float = Field(..., example=75000)

class CompleteRentResponse(ResponseBase[CompleteRentResponseData]):
    """렌트 완료 응답 모델"""
    class Config:
        schema_extra = {
            "example": {
                "resultCode": "SUCCESS",
                "message": "Rental completed successfully",
                "data": {
                    "rent_id": 123,
                    "total_mileage": 150.0,
                    "usage_duration": 3,
                    "estimated_payback_amount": 75000
                }
            }
        }

class RentCostRequest(BaseModel):
    """렌트 비용 계산 요청 모델"""
    rentStartDate: datetime = Field(..., example="2025-01-15T09:00:00")
    rentEndDate: datetime = Field(..., example="2025-01-20T18:00:00")

class RentCostResponseData(BaseModel):
    """렌트 비용 계산 응답 데이터 모델"""
    cost: int = Field(..., example=50000)

class RentCostResponse(ResponseBase[RentCostResponseData]):
    """렌트 비용 계산 응답 모델"""
    class Config:
        schema_extra = {
            "example": {
                "resultCode": "SUCCESS",
                "message": "Rental cost calculated successfully",
                "data": {
                    "cost": 50000
                }
            }
        } 

