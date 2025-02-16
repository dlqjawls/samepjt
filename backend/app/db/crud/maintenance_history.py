from app.db.models.maintenance_history import MaintenanceHistory
from app.db.crud.base import CRUDBase
from sqlmodel import Session, select
from typing import List, Optional, Union, cast
from app.db.models.vehicle import Vehicle
from app.db.models.module import Module
from app.db.models.option import Option
from app.utils.lut_constants import ItemType
from app.utils.exceptions import ConflictError

class MaintenanceHistoryCRUD(CRUDBase[MaintenanceHistory]):
    def __init__(self):
        super().__init__(MaintenanceHistory)
        
    def get_by_id(self, session: Session, maintenance_id: int) -> Optional[MaintenanceHistory]:
        query = select(self.model).where(self.model.maintenance_id == maintenance_id)
        return session.exec(query).first()
        
    def get_item_maintenance_history(self, session: Session, item_id: int, item_type_id: int) -> List[MaintenanceHistory]:
        """주어진 item_id, item_type_id에 해당하는 정비 기록 목록을 조회합니다."""
        query = (
            select(self.model)
            .where(
                self.model.item_id == item_id,
                self.model.item_type_id == item_type_id
            )
        )
        return list(session.exec(query).all())  

    def exists_item_maintenance_history(
        self, session: Session, item_id: int, item_type_id: int, maintenance_status_id: int
    ) -> bool:
        """주어진 item_id, item_type_id, maintenance_status_id에 해당하는 정비 기록 레코드가 존재하는지 확인합니다."""
        query = select(self.model).where(
            self.model.item_id == item_id,
            self.model.item_type_id == item_type_id,
            self.model.maintenance_status_id == maintenance_status_id
        )
        result = session.exec(query).first()
        return result is not None
  
    def fetch_item(self, session: Session, item_type_id: int, item_id: int) -> Optional[Union[Vehicle, Module, Option]]:
        """주어진 item_type_id, item_id에 해당하는 아이템을 조회합니다."""
        mapping = {"vehicle": Vehicle, "module": Module, "option": Option}
        model = mapping.get(ItemType.get_name(item_type_id))
        if model is None:
            raise ConflictError(f"Invalid item type: {ItemType.get_name(item_type_id)  }")
        return cast(Optional[Union[Vehicle, Module, Option]], session.get(model, item_id))
      

maintenance_history_crud = MaintenanceHistoryCRUD()
