from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

from app.models.enum import VideoType


class VideoStorage(SQLModel, table=True):
    videoId: Optional[int] = Field(default=None, primary_key=True)
    rentId: int
    videoType: VideoType
    videoUrl: str
    duration: int
    size: int
    recordedAt: datetime
    createdAt: datetime = Field(default=datetime.now())