from sqlalchemy import text
from sqlmodel import SQLModel, Field, Column, DateTime
from typing import Optional
from datetime import datetime

class Option(SQLModel, table=True):
    __tablename__ = "option"

    option_id: Optional[int] = Field(default=None, primary_key=True)
    option_type_id: int = Field(foreign_key="option_type.option_type_id", nullable=False, description="Option type")

    last_maintenance_at: Optional[datetime] = Field(
        sa_column=Column(DateTime, nullable=True), description="Last maintenance date"
    )
    next_maintenance_at: Optional[datetime] = Field(
        sa_column=Column(DateTime, nullable=True), description="Next scheduled maintenance date"
    )

    item_status_id: int = Field(foreign_key="lut_item_status.item_status_id", nullable=False, description="Option status")

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
