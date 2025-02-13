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

maintenance_history_crud = MaintenanceHistoryCRUD()
