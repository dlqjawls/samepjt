from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

from app.models.enum import RentStatus


class OptionUsageHistory(SQLModel, table=True):
    optionUsageId: Optional[int] = Field(default=None, primary_key=True)
    optionId: int
    rentId: int
    startTime: datetime
    endTime: Optional[datetime] = None
    status: RentStatus
    createdAt: datetime = Field(default=datetime.now())