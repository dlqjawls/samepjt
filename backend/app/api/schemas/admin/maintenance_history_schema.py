from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, validator
from app.api.schemas.common import ResponseBase, Pagination  # Pagination, ResponseBase는 이미 정의되어 있다고 가정

class MaintenanceHistoryItem(BaseModel):
    maintenance_id: int = Field(..., example=301, description="정비 기록 ID")
    item_id: int = Field(..., example=101, description="정비된 항목의 ID")
    item_type_name: str = Field(
        ...,
        example="vehicle",
        description="항목 유형 - vehicle, module, option 중 하나"
    )
    issue: str = Field(..., example="엔진 오일 교체 필요", description="정비 사유 및 문제 설명")
    cost: float = Field(..., example=120.00, description="정비 비용")
    maintenance_status_name: str = Field(
        ...,
        example="pending",
        description="정비 상태 (예: pending, in_progress, completed)"
    )
    scheduled_at: datetime = Field(..., example="2025-01-10T08:00:00", description="정비 예정 날짜")
    completed_at: Optional[datetime] = Field(None, example="2025-01-11T14:00:00", description="정비 완료 날짜 (미완료 시 null)")
    created_at: datetime = Field(..., example="2025-01-05T10:00:00", description="정비 기록 생성 날짜")
    created_by: int = Field(..., example=3, description="정비를 등록한 관리자 ID")
    updated_at: datetime = Field(..., example="2025-01-11T14:00:00", description="정비 기록 마지막 업데이트 날짜")
    updated_by: int = Field(..., example=5, description="마지막으로 정비 기록을 수정한 관리자 ID")

    class Config:
        orm_mode = True

class MaintenanceHistoryData(BaseModel):
    maintenance_history: List[MaintenanceHistoryItem]
    pagination: Pagination

class MaintenanceHistoryGetResponse(ResponseBase[MaintenanceHistoryData]):
    class Config:
        schema_extra = {
            "example": {
                "resultCode": "SUCCESS",
                "message": "Maintenance history retrieved successfully",
                "data": {
                    "maintenance_history": [
                        {
                            "maintenance_id": 301,
                            "item_id": 101,
                            "item_type_name": "vehicle",
                            "issue": "엔진 오일 교체 필요",
                            "cost": 120.00,
                            "maintenance_status_name": "pending",
                            "scheduled_at": "2025-01-10T08:00:00",
                            "completed_at": "2025-01-11T14:00:00",
                            "created_at": "2025-01-05T10:00:00",
                            "created_by": 3,
                            "updated_at": "2025-01-11T14:00:00",
                            "updated_by": 5
                        },
                        {
                            "maintenance_id": 302,
                            "item_id": 101,
                            "item_type_name": "vehicle",
                            "issue": "타이어 점검 필요",
                            "cost": 50.00,
                            "maintenance_status_name": "pending",
                            "scheduled_at": "2025-02-01T10:00:00",
                            "completed_at": None,
                            "created_at": "2025-01-20T12:00:00",
                            "created_by": 3,
                            "updated_at": "2025-02-01T11:00:00",
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

class MaintenanceHistoryPostRequest(BaseModel):
    item_type_name: Literal["vehicle", "module", "option"] = Field(
        ...,
        description="정비 대상 항목 (vehicle, module, option 중 하나)"
    )
    item_id: int = Field(..., gt=0, description="정비 대상의 고유 ID")
    issue: str = Field(..., description="정비 사유 및 문제 설명")
    cost: float = Field(..., ge=0, description="정비 비용 (음수 불가)")
    scheduled_at: Optional[datetime] = Field(
        None, description="정비 예정 날짜, 미제공 시 기본값은 현재 시간"
    )
    completed_at: Optional[datetime] = Field(
        None, description="정비 완료 날짜 (미완료 시 null)"
    )

class MaintenanceHistoryPostResponse(ResponseBase):
    class Config:
        schema_extra = {
            "example": {
                "resultCode": "SUCCESS",
                "message": "Maintenance history created successfully"
            }
        }

class MaintenanceHistoryPatchRequest(BaseModel):
    maintenance_status_id: Optional[int] = Field(
        None,
        ge=1,
        le=3,
        description="정비 상태 ID (1: pending, 2: in_progress, 3: completed)"
    )
    cost: Optional[float] = Field(
        None,
        ge=0,
        description="정비 비용 (0 이상)"
    )
    scheduled_at: Optional[datetime] = Field(
        None,
        description="정비 예정 날짜 (YYYY-MM-DDTHH:mm:ss)"
    )
    completed_at: Optional[datetime] = Field(
        None,
        description="정비 완료 날짜 (YYYY-MM-DDTHH:mm:ss, 완료 상태일 경우 필수)"
    )
    issue: Optional[str] = Field(
        None,
        description="정비 이슈 설명"
    )

class MaintenanceHistoryPatchResponse(ResponseBase):
    class Config:
        schema_extra = {
            "example": {
                "resultCode": "SUCCESS",
                "message": "Maintenance history updated successfully"
            }
        }

class MaintenanceHistoryDeleteResponse(ResponseBase):
    class Config:
        schema_extra = {
            "example": {
                "resultCode": "SUCCESS",
                "message": "Maintenance history deleted successfully"
            }
        } 