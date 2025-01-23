from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class User(SQLModel, table=True):
    userPK: Optional[int] = Field(default=None, primary_key=True)
    userId: str = Field(index=True, unique=True)
    userPassword: str
    userEmail: str = Field(index=True, unique=True)
    userName: str
    userPhoneNum: str
    userAddress: str
    createdAt: datetime = Field(default_factory=datetime.now)
    updatedAt: datetime = Field(default_factory=datetime.now)