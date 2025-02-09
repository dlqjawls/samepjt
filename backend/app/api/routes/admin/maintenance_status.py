from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.api.schemas.admin.maintenance_status_schema import MaintenanceStatusResponse
from app.core.database import get_session
from app.core.jwt import JWTPayload, jwt_handler
from app.services.admin.maintenance_status_service import MaintenanceStatusService

router = APIRouter(
)

@router.get(
    "/maintenance-status",
    response_model=MaintenanceStatusResponse,
    summary="정비 기록 상태 조회",
    description="관리자가 등록된 정비 기록 상태 목록을 조회합니다."
)
def get_maintenance_statuses(
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency(allowed_roles=["semi", "master"]))
):
    return MaintenanceStatusService.get_maintenance_statuses(session) 