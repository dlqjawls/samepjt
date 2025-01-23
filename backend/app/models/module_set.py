from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from app.models.module_set_option_type import ModuleSetOptionType  # Add this import

if TYPE_CHECKING:
    from app.models.option_type import OptionType

class ModuleSet(SQLModel, table=True):
    """ 모듈 세트 모델 """
    moduleSetId: Optional[int] = Field(default=None, primary_key=True)
    moduleSetName: str
    description: Optional[str] = None
    moduleSetImages: str
    moduleSetFeatures: str
    basePrice: float
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    optionTypes: List["OptionType"] = Relationship(
        back_populates="moduleSets",
        link_model=ModuleSetOptionType
    )