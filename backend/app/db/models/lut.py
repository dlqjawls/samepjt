from sqlmodel import SQLModel, Field
from typing import Optional

# 역할 테이블 (master, semi, user)
class Role(SQLModel, table=True):
    __tablename__ = "lut_roles"

    role_id: Optional[int] = Field(default=None, primary_key=True)
    role_name: str = Field(unique=True, nullable=False, max_length=50)


# 아이템 상태 테이블 (active, inactive, maintenance)
class ItemStatus(SQLModel, table=True):
    __tablename__="lut_item_status"

    item_status_id: Optional[int] = Field(default=None, primary_key=True)
    item_status_name: str = Field(unique=True, nullable=False, max_length=50)


# 아이템 유형 테이블 (vehicle, module, option)
class ItemType(SQLModel, table=True):
    __tablename__="lut_item_type"

    item_type_id: Optional[int] = Field(default=None, primary_key=True)
    item_type_name: str = Field(unique=True, nullable=False, max_length=50)


# 모듈 유형 테이블 (small, medium, large)
class ModuleType(SQLModel, table=True):
    __tablename__="lut_module_type"

    module_type_id: Optional[int] = Field(default=None, primary_key=True)
    module_type_name: str = Field(unique=True, nullable=False, max_length=50)
    module_type_size: str = Field(nullable=False, max_length=50)
    module_type_cost: float = Field(nullable=False, gt=0, description="Module cost must be greater than zero")


# 유지보수 상태 테이블 (pending, in_progress, completed)
class MaintenanceStatus(SQLModel, table=True):
  __tablename__="lut_maintenance_status"

  maintenance_status_id: Optional[int] = Field(default=None, primary_key=True)
  maintenance_status_name: str = Field(unique=True, nullable=False, max_length=50)


# 사용 기록 상태 테이블 (in_use, completed)
class UsageStatus(SQLModel, table=True):
  __tablename__="lut_usage_status"

  usage_status_id: Optional[int] = Field(default=None, primary_key=True)
  usage_status_name: str = Field(unique=True, nullable=False, max_length=50)


# 대여 상태 테이블 (in_progress, completed, canceled)
class RentStatus(SQLModel, table=True):
  __tablename__="lut_rent_status"

  rent_status_id: Optional[int] = Field(default=None, primary_key=True)
  rent_status_name: str = Field(unique=True, nullable=False, max_length=50)


# 비디오 유형 테이블 (module, autonomous driving)
class VideoType(SQLModel, table=True):
  __tablename__="lut_video_type"

  video_type_id: Optional[int] = Field(default=None, primary_key=True)
  video_type_name: str = Field(unique=True, nullable=False, max_length=50)


# 결제 상태 테이블 (pending, completed, failed, refunded)
class PaymentStatus(SQLModel, table=True):
  __tablename__="lut_payment_status"

  payment_status_id: Optional[int] = Field(default=None, primary_key=True)
  payment_status_name: str = Field(unique=True, nullable=False, max_length=50)


# 결제 방식 테이블 (credit_card, bank_transfer, paypal)
class PaymentMethod(SQLModel, table=True):
  __tablename__="lut_payment_method"

  payment_method_id: Optional[int] = Field(default=None, primary_key=True)
  payment_method_name: str = Field(unique=True, nullable=False, max_length=50)
