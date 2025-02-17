from sqlalchemy import text
from sqlmodel import SQLModel, Field, Column, DateTime
from typing import Optional
from datetime import datetime

class Payment(SQLModel, table=True):
    __tablename__ = "payment"

    payment_id: Optional[int] = Field(default=None, primary_key=True)
    rent_id: int = Field(foreign_key="rent_history.rent_id", nullable=False, description="Associated Rent ID")
    
    cost: float = Field(nullable=False, description="Payment cost (>= 0)")
    payment_status_id: int = Field(foreign_key="lut_payment_status.payment_status_id", nullable=False, description="Payment status")
    payment_method_id: int = Field(foreign_key="lut_payment_method.payment_method_id", nullable=False, description="Payment method")

    created_at: datetime = Field(
        sa_column=Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"), onupdate=datetime.now)
    )
