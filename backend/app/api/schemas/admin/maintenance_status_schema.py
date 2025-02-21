from pydantic import BaseModel, Field
from typing import List
from app.api.schemas.common import ResponseBase


class MaintenanceStatusItem(BaseModel):
    maintenance_status_id: int = Field(..., example=1)
    maintenance_status_name: str = Field(..., example="pending")

class MaintenanceStatusData(BaseModel):
    maintenance_statuses: List[MaintenanceStatusItem]

class MaintenanceStatusResponse(ResponseBase[MaintenanceStatusData]):
    class Config:
        schema_extra = {
            "example": {
                "resultCode": "SUCCESS",
                "message": "Maintenance statuses retrieved successfully",
                "data": {"maintenance_statuses": [{"maintenance_status_id": 1, "maintenance_status_name": "pending"}]}
            }
        }
      