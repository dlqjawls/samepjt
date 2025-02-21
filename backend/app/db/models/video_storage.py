from sqlmodel import SQLModel, Field, Column, DateTime
from typing import Optional
from datetime import datetime
from sqlalchemy import text


class VideoStorage(SQLModel, table=True): 
    __tablename__ = "video_storage"

    video_id: Optional[int] = Field(default=None, primary_key=True)
    rent_id: int = Field(foreign_key="rent_history.rent_id", nullable=False, description="Associated Rent ID")
    
    video_type_id: int = Field(foreign_key="lut_video_type.video_type_id", nullable=False, description="Video Type ID")
    video_url: str = Field(nullable=False, max_length=500, description="URL of the stored video")

    created_at: datetime = Field(
        sa_column=Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    )
