from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
from app.api.schemas.common import Coordinate, ResponseBase, Pagination


class RentHistoryItem(BaseModel):
    """렌트 히스토리 개별 항목"""
    rent_id: int = Field(..., example=101)
    user_pk: int = Field(..., example=3)
    vehicle_number: str = Field(..., example="PBV-1234")
    option_types: str = Field(..., example="1,2,3")
    departure_location: Coordinate = Field(..., example={"x": 11.512, "y": 30.4531})
    arrival_location: Coordinate = Field(..., example={"x": 11.512, "y": 30.4531})
    cost: float = Field(..., example=150.00)
    mileage: float = Field(..., example=450.5)
    rent_status_name: str = Field(..., example="In-progress")
    created_at: datetime = Field(..., example="2025-02-01T10:00:00")
    updated_at: datetime = Field(..., example="2025-02-01T15:00:00")


class RentHistoryData(BaseModel):
    """렌트 히스토리 데이터"""
    rent_history: List[RentHistoryItem]
    pagination: Pagination

class RentHistoryResponse(ResponseBase[RentHistoryData]):
    """렌트 히스토리 응답 모델"""
    class Config:
        schema_extra = {
            "example": {
                "resultCode": "SUCCESS",
                "message": "Rent logs retrieved successfully",
                "data": {
                    "rent_history": [
                        {
                            "rent_id": 1,
                            "user_pk": 1,
                            "vehicle_number": "PBV-00001",
                            "option_types": "",
                            "departure_location": {
                              "x": 11.512,
                              "y": 30.4531
                            },
                            "arrival_location": {
                              "x": 12.313,
                              "y": 32.3232
                            },
                            "cost": 500,
                            "mileage": 0,
                            "rent_status_name": "in_progress",
                            "created_at": "2025-02-11T02:30:24.614775",
                            "updated_at": "2025-02-11T02:30:24.614775"
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
        
        
        
class RentVideoItem(BaseModel):
    video_id: int = Field(..., example=501)
    rent_id: int = Field(..., example=101)
    # video_type 필드를 통해 'autonomous driving' 또는 'module installation' 으로 구분
    video_type: str = Field(
        ...,
        example="autonomous driving",
        description="영상 유형. 'autonomous driving' 또는 'module installation' 중 하나"
    )
    video_url: str = Field(..., example="https://example.com/videos/501.mp4")
    recorded_at: datetime = Field(..., example="2025-02-01T10:00:00")

class RentVideoData(BaseModel):
    videos: List[RentVideoItem]

class RentVideoResponse(ResponseBase[RentVideoData]):
    class Config:
        schema_extra = {
            "example": {
                "resultCode": "SUCCESS",
                "message": "Videos retrieved successfully",
                "data": {
                    "videos": [
                        {
                            "video_id": 501,
                            "rent_id": 101,
                            "video_type": "autonomous driving",
                            "video_url": "https://example.com/videos/501.mp4",
                            "recorded_at": "2025-02-01T10:00:00"
                        },
                        {
                            "video_id": 602,
                            "rent_id": 101,
                            "video_type": "module installation",
                            "video_url": "https://example.com/videos/602.mp4",
                            "recorded_at": "2025-02-01T10:15:00"
                        }
                    ]
                }
            }
        } 