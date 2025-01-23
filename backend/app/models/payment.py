from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

from app.models.enum import PaymentStatus


class Payment(SQLModel, table=True):
    paymentId: Optional[int] = Field(default=None, primary_key=True)
    rentId: int
    amount: float
    status: PaymentStatus
    paymentMethod: str
    paymentDate: datetime
    refundAmount: Optional[float] = None
    refundDate: Optional[datetime] = None
    createdAt: datetime = Field(default=datetime.now())
    updatedAt: datetime = Field(default=datetime.now())