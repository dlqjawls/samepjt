from sqlmodel import Session, select, SQLModel
from typing import Optional, Type, TypeVar, Generic, List
from app.models.lut import Role, ItemStatus, ItemType, ModuleType, MaintenanceStatus, UsageStatus, RentStatus, VideoType, PaymentStatus, PaymentMethod
from app.utils.lut_constants import (
    ROLE_MAPPING,
    ITEM_STATUS_MAPPING,
    ITEM_TYPE_MAPPING,
    MODULE_TYPE_MAPPING,
    MAINTENANCE_STATUS_MAPPING,
    USAGE_STATUS_MAPPING,
    RENT_STATUS_MAPPING,
    VIDEO_TYPE_MAPPING,
    PAYMENT_STATUS_MAPPING,
    PAYMENT_METHOD_MAPPING
)

T = TypeVar("T", bound=SQLModel)

class LookUpTableCRUD(Generic[T]):
    def __init__(self, model: Type[T], id_field: str):
        self.model = model
        self.id_field = id_field

    def get_all(self, session: Session) -> List[T]:
        return list(session.exec(select(self.model)).all())

    def get_by_id(self, session: Session, id: int) -> Optional[T]:
        result = session.exec(select(self.model).where(getattr(self.model, self.id_field) == id)).first()
        return result

role = LookUpTableCRUD(Role, "role_id")
item_status = LookUpTableCRUD(ItemStatus, "item_status_id")
item_type = LookUpTableCRUD(ItemType, "item_type_id")
module_type = LookUpTableCRUD(ModuleType, "module_type_id")
maintenance_status = LookUpTableCRUD(MaintenanceStatus, "maintenance_status_id")
usage_status = LookUpTableCRUD(UsageStatus, "usage_status_id")
rent_status = LookUpTableCRUD(RentStatus, "rent_status_id")
video_type = LookUpTableCRUD(VideoType, "video_type_id")
payment_status = LookUpTableCRUD(PaymentStatus, "payment_status_id")
payment_method = LookUpTableCRUD(PaymentMethod, "payment_method_id")

def get_role_mapping() -> dict:
    """역할(Role) LUT 상수를 반환합니다."""
    return ROLE_MAPPING

def get_item_status_mapping() -> dict:
    """아이템 상태(Item Status) LUT 상수를 반환합니다."""
    return ITEM_STATUS_MAPPING

def get_item_type_mapping() -> dict:
    """아이템 유형(Item Type) LUT 상수를 반환합니다."""
    return ITEM_TYPE_MAPPING

def get_module_type_mapping() -> dict:
    """모듈 유형(Module Type) LUT 상수를 반환합니다."""
    return MODULE_TYPE_MAPPING

def get_maintenance_status_mapping() -> dict:
    """유지보수 상태(Maintenance Status) LUT 상수를 반환합니다."""
    return MAINTENANCE_STATUS_MAPPING

def get_usage_status_mapping() -> dict:
    """사용 기록 상태(Usage Status) LUT 상수를 반환합니다."""
    return USAGE_STATUS_MAPPING

def get_rent_status_mapping() -> dict:
    """대여 상태(Rent Status) LUT 상수를 반환합니다."""
    return RENT_STATUS_MAPPING

def get_video_type_mapping() -> dict:
    """비디오 유형(Video Type) LUT 상수를 반환합니다."""
    return VIDEO_TYPE_MAPPING

def get_payment_status_mapping() -> dict:
    """결제 상태(Payment Status) LUT 상수를 반환합니다."""
    return PAYMENT_STATUS_MAPPING

def get_payment_method_mapping() -> dict:
    """결제 방식(Payment Method) LUT 상수를 반환합니다."""
    return PAYMENT_METHOD_MAPPING