from sqlalchemy import text
from sqlmodel import SQLModel, Field, Column, DateTime
from typing import Optional
from datetime import datetime

class OptionType(SQLModel, table=True):
    __tablename__ = "option_type"

    option_type_id: Optional[int] = Field(default=None, primary_key=True)
    option_type_name: str = Field(nullable=False, max_length=100, description="Option Type Name")
    option_type_size: str = Field(nullable=False, max_length=50, description="Option Type Size")
    option_type_cost: float = Field(nullable=False, description="Option Cost (>= 0)")

    description: Optional[str] = Field(default=None, description="Option Description")
    option_type_images: str = Field(nullable=False, description="Images of the Option Type")
    option_type_features: str = Field(nullable=False, description="Features of the Option Type")

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
