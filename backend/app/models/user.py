from sqlmodel import SQLModel, Field, Column
from sqlalchemy import DateTime, event
from typing import Optional
from datetime import datetime

class User(SQLModel, table=True):
    user_pk: Optional[int] = Field(
        default=None, 
        primary_key=True
    )
    user_id: str = Field(unique=True, nullable=False, max_length=50)
    user_password: str = Field(nullable=False, max_length=255, description="Encrypted password")
    user_email: str = Field(unique=True, nullable=False, max_length=100)
    user_name: str = Field(nullable=False, max_length=100)
    user_phone_num: str = Field(nullable=False, max_length=20)
    user_address: str = Field(nullable=False)
    role_id: int = Field(foreign_key="lut_roles.role_id", nullable=False)

    created_at: datetime = Field(
        sa_column=Column("created_at", DateTime, nullable=False, server_default="CURRENT_TIMESTAMP")
    )
    created_by: Optional[int] = Field(
        foreign_key="user.user_pk", 
        nullable=True, 
        description="생성한 사용자"
    )
    updated_at: datetime = Field(
        sa_column=Column("updated_at", DateTime, nullable=False, server_default="CURRENT_TIMESTAMP")
    )
    updated_by: Optional[int] = Field(
        foreign_key="user.user_pk", 
        nullable=True, 
        description="수정한 사용자"
    )
    deleted_at: Optional[datetime] = Field(
        default=None, 
        sa_column=Column("deleted_at", DateTime, nullable=True)
    )

    __table_args__ = {"sqlite_autoincrement": True}


# ✅ 자동으로 created_by를 user_pk로 설정하는 이벤트 핸들러
@event.listens_for(User, "before_insert")
def set_created_by(mapper, connection, target):
    if target.created_by is None and target.user_pk:
        target.created_by = target.user_pk  # 🔥 user_pk를 created_by로 자동 할당


# ✅ 자동으로 updated_by를 user_pk로 설정하는 이벤트 핸들러
@event.listens_for(User, "before_update")
def set_updated_by(mapper, connection, target):
    if target.updated_by is None and target.user_pk:
        target.updated_by = target.user_pk  # 🔥 user_pk를 updated_by로 자동 할당
