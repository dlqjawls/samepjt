from sqlmodel import Session
from app.api.schemas.admin.maintenance_status_schema import (
    MaintenanceStatusResponse,
    MaintenanceStatusData,
    MaintenanceStatusItem
)
from app.db.crud.lut import maintenance_status

class MaintenanceStatusService:
    @staticmethod
    def get_maintenance_statuses(session: Session) -> MaintenanceStatusResponse:
        """관리자가 등록된 정비 기록 상태 목록을 조회합니다."""
        # DB에서 정비 상태 목록을 조회합니다.
        statuses_from_db = maintenance_status.get_all(session)
        statuses = [
            MaintenanceStatusItem(
                maintenance_status_id=status.maintenance_status_id,
                maintenance_status_name=status.maintenance_status_name
            )
            for status in statuses_from_db
        ]
        data = MaintenanceStatusData(maintenance_statuses=statuses)
        return MaintenanceStatusResponse(
            resultCode="SUCCESS",
            message="Maintenance statuses retrieved successfully",
            data=data
        )