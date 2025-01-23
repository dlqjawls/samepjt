from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

from app.models.enum import ItemStatus

class Module(SQLModel, table=True):
  moduleId: Optional[int] = Field(default=None, primary_key=True)
  moduleNfcTagId: str = Field(index=True, unique=True)
  moduleType: str
  moduleSize: str
  moduleCost: float
  status: ItemStatus = Field(default="INACTIVE")
  lastMaintenanceAt: Optional[datetime] = None
  nextMaintenanceAt: Optional[datetime] = None
  currentLocation: str
  createdAt: datetime = Field(default=datetime.now())
  updatedAt: datetime = Field(default=datetime.now())