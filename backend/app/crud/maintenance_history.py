from app.models.maintenance_history import MaintenanceHistory
from app.crud.base import CRUDBase

class MaintenanceHistoryCRUD(CRUDBase[MaintenanceHistory]):
    def __init__(self):
        super().__init__(MaintenanceHistory, "maintenance_id")

    def get_maintenance_status_name(self, status_id: int) -> str:
        """
        주어진 유지보수 상태 ID에 해당하는 이름을 반환합니다.
        """
        from app.crud.lut import get_maintenance_status_mapping
        mapping = get_maintenance_status_mapping()
        return mapping.get(status_id, "Unknown")

maintenance_history_crud = MaintenanceHistoryCRUD()
