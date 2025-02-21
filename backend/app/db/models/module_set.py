from sqlalchemy import text
from sqlmodel import SQLModel, Field, Column, DateTime
from typing import Optional
from datetime import datetime

class ModuleSet(SQLModel, table=True):
    __tablename__ = "module_set"

    module_set_id: Optional[int] = Field(default=None, primary_key=True)
    module_set_name: str = Field(nullable=False, max_length=100, description="Module Set Name")

    description: Optional[str] = Field(default=None, description="Module Set Description")
    module_set_images: Optional[str] = Field(default=None, description="Module Set Images")
    module_set_features: Optional[str] = Field(default=None, description="Module Set Features")
    module_type_id: int = Field(foreign_key="lut_module_type.module_type_id", nullable=False, description="Module Type ID")

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
