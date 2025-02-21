from sqlmodel import SQLModel, Field, Column, DateTime
from typing import Optional
from datetime import datetime
from sqlalchemy import text

class MaintenanceHistory(SQLModel, table=True):
    __tablename__ = "maintenance_history"

    maintenance_id: Optional[int] = Field(default=None, primary_key=True)

    item_id: int = Field(nullable=False, description="ID of the maintained item")
    item_type_id: int = Field(foreign_key="lut_item_type.item_type_id", nullable=False, description="Item Type ID")

    issue: str = Field(nullable=False, description="Maintenance issue details")
    cost: float = Field(nullable=False, description="Maintenance cost (>= 0)")

    maintenance_status_id: int = Field(foreign_key="lut_maintenance_status.maintenance_status_id", nullable=False, description="Maintenance status")
    scheduled_at: datetime = Field(default=None, description="Scheduled maintenance date")
    completed_at: Optional[datetime] = Field(default=None, description="Completion date")

    created_at: datetime = Field(
        sa_column=Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    )
    created_by: int = Field(foreign_key="user.user_pk", nullable=False, description="User who created this record")

    updated_at: datetime = Field(
        sa_column=Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"), onupdate=datetime.now)
    )
    updated_by: int = Field(foreign_key="user.user_pk", nullable=False, description="User who last updated this record")

    deleted_at: Optional[datetime] = Field(
        sa_column=Column(DateTime, nullable=True)
    )
