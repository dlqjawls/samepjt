from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from app.models.module_set_option_type import ModuleSetOptionType  # Add this import

if TYPE_CHECKING:
    from app.models.module_set import ModuleSet

class OptionType(SQLModel, table=True):
    """ 옵션 타입 모델 """
    optionTypeId: Optional[int] = Field(default=None, primary_key=True)
    optionTypeName: str
    optionTypeSize: str
    optionTypeCost: float
    description: Optional[str] = None
    optionTypeImages: str
    optionTypeFeatures: str
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    moduleSets: List["ModuleSet"] = Relationship(
        back_populates="optionTypes",
        link_model=ModuleSetOptionType
    )