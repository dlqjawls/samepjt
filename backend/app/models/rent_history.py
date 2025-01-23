from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

from app.models.enum import RentStatus

class RentHistory(SQLModel, table=True):
    rentId: Optional[int] = Field(default=None, primary_key=True)
    userPK: int
    departureLocation: str
    arrivalLocation: str
    rentStatus: RentStatus = Field(default="IN_PROGRESS")
    startTime: datetime
    endTime: Optional[datetime] = None
    baseCost: float
    additionalCost: float = Field(default=0)
    totalDistance: float = Field(default=0)
    statusUpdatedAt: datetime
    createdAt: datetime = Field(default=datetime.now())