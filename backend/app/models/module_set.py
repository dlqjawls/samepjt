from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class ModuleSet(SQLModel, table=True):
    moduleSetId: Optional[int] = Field(default=None, primary_key=True)
    moduleSetName: str
    description: str = None
    module_sets_images: str
    module_sets_features: str
    basePrice: float
    createdAt: datetime = Field(default=datetime.now())
    updatedAt: datetime = Field(default=datetime.now())