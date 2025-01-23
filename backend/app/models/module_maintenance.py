from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

from app.models.enum import MaintenanceStatus

class ModuleMaintenance(SQLModel, table=True):
    maintenanceId: Optional[int] = Field(default=None, primary_key=True)
    adminPK: int
    moduleId: int
    issue: str
    maintenanceDate: datetime
    cost: float
    status: MaintenanceStatus
    completedAt: Optional[datetime] = None
    notes: Optional[str] = None
    createdAt: datetime = Field(default=datetime.now())
    updatedAt: datetime = Field(default=datetime.now())