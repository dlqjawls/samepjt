from datetime import datetime
from sqlmodel import SQLModel, Field
from typing import Optional

from app.models.enum import ItemStatus


class Option(SQLModel, table=True):
    optionId: Optional[int] = Field(default=None, primary_key=True)
    optionType: int
    status: ItemStatus = Field(default="INACTIVE")
    createdAt: datetime = Field(default=datetime.now())
    updatedAt: datetime = Field(default=datetime.now())