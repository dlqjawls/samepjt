from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class ModuleSetOptionType(SQLModel, table=True):
    """ 모듈 세트와 옵션 타입 간의 N:M 관계 테이블 """
    moduleSetId: Optional[int] = Field(default=None, foreign_key="moduleset.moduleSetId", primary_key=True)
    optionTypeId: Optional[int] = Field(default=None, foreign_key="optiontype.optionTypeId", primary_key=True)
    quantity: int = Field(default=1)
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)