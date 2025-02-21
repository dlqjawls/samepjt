from sqlalchemy import text
from sqlmodel import SQLModel, Field, Column, DateTime
from typing import Optional
from datetime import datetime

class UsageHistory(SQLModel, table=True):
    __tablename__ = "usage_history"

    usage_id: Optional[int] = Field(default=None, primary_key=True)
    rent_id: int = Field(foreign_key="rent_history.rent_id", nullable=False, description="Associated Rent ID")
    item_id: int = Field(nullable=False, description="ID of the used item")
    item_type_id: int = Field(foreign_key="lut_item_type.item_type_id", nullable=False, description="Item Type ID")
    
    usage_status_id: int = Field(foreign_key="lut_usage_status.usage_status_id", nullable=False, description="Usage status")

    created_at: datetime = Field(
        sa_column=Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"), onupdate=datetime.now())
    )