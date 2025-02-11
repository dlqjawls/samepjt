from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.core.database import get_session
from app.core.jwt import JWTPayload, jwt_handler
from app.services.admin.dashboard_service import DashboardService
from app.api.schemas.admin.dashboard_overall_schema import DashboardOverallResponse, DashboardData

router = APIRouter(prefix="/admin/dashboard", tags=["Dashboard"])

@router.get(
    "",
    response_model=DashboardOverallResponse,
    summary="관리자 대시보드 조회",
    description="상단 카드, 상태 차트, 판매 통계, 모듈 및 옵션 선호도 정보를 포함한 대시보드 데이터를 조회합니다."
)
def get_overall_dashboard(
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency(allowed_roles=["master"]))
):
    dashboard_data: DashboardData = DashboardData(**DashboardService.get_overall_dashboard_data(session))
    return DashboardOverallResponse.success(
        message="Dashboard data retrieved successfully",
        data=dashboard_data
    ) 