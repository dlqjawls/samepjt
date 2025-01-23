from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class ModuleSetOptionType(SQLModel, table=True):
    moduleSetId: Optional[int] = Field(default=None, primary_key=True)
    optionTypeId: Optional[int] = Field(default=None, primary_key=True)
    quantity: int = Field(default=1)
    createdAt: datetime = Field(default=datetime.now())
    updatedAt: datetime = Field(default=datetime.now())