from app.db.models.maintenance_history import MaintenanceHistory
from app.db.crud.base import CRUDBase
from sqlmodel import Session, select
from typing import List

class MaintenanceHistoryCRUD(CRUDBase[MaintenanceHistory]):
    def __init__(self):
        super().__init__(MaintenanceHistory)
        
    def get_item_maintenance_history(self, session: Session, item_id: int, item_type_id: int) -> List[MaintenanceHistory]:
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


maintenance_history_crud = MaintenanceHistoryCRUD()
