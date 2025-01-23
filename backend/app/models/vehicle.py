from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

from app.models.enum import ItemStatus

class Vehicle(SQLModel, table=True):
  vehicleId: Optional[int] = Field(default=None, primary_key=True)
  vin: str
  vehicleNumber: str
  currentLocation: str
  status: ItemStatus = Field(default="INACTIVE")
  mileage: float = Field(default=0)
  lastMaintenanceAt: Optional[datetime] = None
  nextMaintenanceAt: Optional[datetime] = None
  createdAt: datetime = Field(default=datetime.now())
  updatedAt: datetime = Field(default=datetime.now())