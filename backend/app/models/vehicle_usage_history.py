from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

from app.models.enum import RentStatus


class VehicleUsageHistory(SQLModel, table=True):
    vehicleUsageId: Optional[int] = Field(default=None, primary_key=True)
    vehicleId: int
    rentId: int
    startLocation: str
    endLocation: str
    startTime: datetime
    endTime: Optional[datetime] = None
    status: RentStatus
    mileage: float
    createdAt: datetime = Field(default=datetime.now())