from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class OptionType(SQLModel, table=True):
    optionTypeId: Optional[int] = Field(default=None, primary_key=True)
    optionTypeName: str
    optionTypeSize: str
    optionTypeCost: float
    description: str = None
    optionTypeimages: str
    optionTypefeatures: str
    createdAt: datetime = Field(default=datetime.now())
    updatedAt: datetime = Field(default=datetime.now())