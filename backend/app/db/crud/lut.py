from sqlmodel import Session, select, SQLModel
from typing import Optional, Type, TypeVar, Generic, List
from app.db.models.lut import Role, ItemStatus, ItemType, ModuleType, MaintenanceStatus, UsageStatus, RentStatus, VideoType, PaymentStatus, PaymentMethod

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