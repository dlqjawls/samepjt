from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

from app.models.enum import RentStatus


class ModuleUsageHistory(SQLModel, table=True):
    moduleUsageId: Optional[int] = Field(default=None, primary_key=True)
    moduleId: int
    rentId: int
    startTime: datetime
    endTime: Optional[datetime] = None
    status: RentStatus
    createdAt: datetime = Field(default=datetime.now())