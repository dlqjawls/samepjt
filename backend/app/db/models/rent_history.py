from sqlmodel import SQLModel, Field, Column, DateTime
from typing import Optional
from datetime import datetime
from sqlalchemy import text

class RentHistory(SQLModel, table=True):
    __tablename__ = "rent_history"

    rent_id: Optional[int] = Field(default=None, primary_key=True)
    user_pk: int = Field(foreign_key="user.user_pk", nullable=False, description="User who rented the item")
    
    departure_location: str = Field(nullable=False, max_length=255, description="Departure location")
    arrival_location: str = Field(nullable=False, max_length=255, description="Arrival location")
    
    cost: float = Field(nullable=False, description="Total rental cost (>= 0)")
    mileage: float = Field(default=0, nullable=False, description="Total mileage during rental")
    
    rent_start_date: datetime = Field(nullable=True, description="Rental start date")
    rent_end_date: datetime = Field(nullable=True, description="Rental end date")
    
    rent_status_id: int = Field(foreign_key="lut_rent_status.rent_status_id", nullable=False, description="Rental status")
    
    created_at: datetime = Field(
        sa_column=Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"), onupdate=datetime.now)
    )
