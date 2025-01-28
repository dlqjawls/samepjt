from app.models.maintenance_history import MaintenanceHistory
from app.crud.base import CRUDBase

class MaintenanceHistoryCRUD(CRUDBase[MaintenanceHistory]):
    def __init__(self):
        super().__init__(MaintenanceHistory, "maintenance_id")

maintenance_history_crud = MaintenanceHistoryCRUD()
