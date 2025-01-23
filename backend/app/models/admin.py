from datetime import datetime
from sqlalchemy import Enum
from sqlmodel import SQLModel, Field
from typing import Optional

from app.models.enum import AdminRole

class Admin(SQLModel, table=True):
    adminPK: Optional[int] = Field(default=None, primary_key=True)
    adminId: str = Field(index=True, unique=True)
    adminPassword: str
    role: AdminRole = Field(default="SEMI")
    createdAt: datetime = Field(default_factory=datetime.now)
    updatedAt: datetime = Field(default_factory=datetime.now)