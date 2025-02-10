from sqlmodel import SQLModel, Field, Column, DateTime
from typing import Optional
from datetime import datetime
from sqlalchemy import text

class Vehicle(SQLModel, table=True):
    __tablename__ = "vehicle"

    vehicle_id: Optional[int] = Field(default=None, primary_key=True)
    vin: str = Field(unique=True, nullable=False, max_length=50, description="Vehicle Identification Number")
    vehicle_number: str = Field(unique=True, nullable=False, max_length=50, description="License Plate Number")
    current_location: str = Field(nullable=False, max_length=255, description="Current vehicle location")
    mileage: float = Field(default=0, nullable=False, description="Total vehicle mileage")
    
    last_maintenance_at: Optional[datetime] = Field(
        sa_column=Column(DateTime, nullable=True), description="Last maintenance date"
    )
    next_maintenance_at: Optional[datetime] = Field(
        sa_column=Column(DateTime, nullable=True), description="Next scheduled maintenance date"
    )

    item_status_id: int = Field(foreign_key="lut_item_status.item_status_id", nullable=False, description="Vehicle status (Active, Inactive, Maintenance)")


    created_at: datetime = Field(
        sa_column=Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    )
    created_by: int = Field(foreign_key="user.user_pk", nullable=False, description="User who created this record")
    
    updated_at: datetime = Field(
        sa_column=Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"), onupdate=datetime.now)
    )
    updated_by: int = Field(foreign_key="user.user_pk", nullable=False, description="User who last updated this record")
    
    deleted_at: Optional[datetime] = Field(
        sa_column=Column(DateTime, nullable=True), description="Soft delete timestamp"
    )

    __table_args__ = {"sqlite_autoincrement": True}
