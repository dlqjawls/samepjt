from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.core.database import get_session
from app.core.jwt import JWTPayload, jwt_handler
from app.services.admin.dashboard_service import DashboardService
from app.api.schemas.admin.dashboard_schema import (
    CountResponse,
    ChartListResponse,
    RentalCountListResponse,
    MaintenanceCostListResponse,
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

# ── 차량 관련 엔드포인트 ──

@router.get(
    "/vehicles/today-rented-count",
    response_model=CountResponse,
    summary="오늘 대여된 차량 수 조회",
    description="오늘 대여된 차량 수를 조회합니다."
)
def get_today_rented_vehicles(
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency(allowed_roles=["master", "semi"]))
):
    count = DashboardService.get_today_rented_vehicles_count(session)
    return CountResponse.success(message="Today rented vehicles Count retrieved successfully", data=count)

@router.get(
    "/vehicles/currently-renting-count",
    response_model=CountResponse,
    summary="현재 대여 중인 차량 수 조회",
    description="현재 대여 중인 차량 수를 조회합니다."
)
def get_currently_renting_vehicles(
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency(allowed_roles=["master", "semi"]))
):
    count = DashboardService.get_currently_renting_vehicles_count(session)
    return CountResponse.success(message="Currently renting vehicles Count retrieved successfully", data=count)

@router.get(
    "/vehicles/today-expected-return-count",
    response_model=CountResponse,
    summary="오늘 예상 반납 차량 수 조회",
    description="오늘 예상 반납 차량 수를 조회합니다."
)
def get_today_expected_return_vehicles(
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency(allowed_roles=["master", "semi"]))
):
    count = DashboardService.get_today_expected_return_vehicles_count(session)
    return CountResponse.success(message="Today expected return vehicles count retrieved", data=count)

@router.get(
    "/vehicles/state-chart",
    response_model=ChartListResponse,
    summary="차량 상태 차트 조회",
    description="차량 상태 분포 차트를 조회합니다."
)
def get_vehicle_state_chart(
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency(allowed_roles=["master", "semi"]))
):
    chart = DashboardService.get_vehicle_state_chart(session)
    return ChartListResponse.success(message="Vehicle state data retrieved successfully", data=chart)

# ── 모듈 관련 엔드포인트 ──

@router.get(
    "/modules/state-chart",
    response_model=ChartListResponse,
    summary="모듈 상태 차트 조회",
    description="모듈 상태 분포 차트를 조회합니다."
)
def get_module_state_chart(
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency(allowed_roles=["master", "semi"]))
):
    chart = DashboardService.get_module_state_chart(session)
    return ChartListResponse.success(message="Module state data retrieved successfully", data=chart)

# ── 옵션 관련 엔드포인트 ──

@router.get(
    "/options/state-chart",
    response_model=ChartListResponse,
    summary="옵션 상태 차트 조회",
    description="옵션 상태 분포 차트를 조회합니다."
)
def get_option_state_chart(
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency(allowed_roles=["master", "semi"]))
):
    chart = DashboardService.get_option_state_chart(session)
    return ChartListResponse.success(message="Option state data retrieved successfully", data=chart)

# ── 판매 통계 관련 엔드포인트 ──

@router.get(
    "/sales/rental-counts",
    response_model=RentalCountListResponse,
    summary="월별 대여 건수 조회",
    description="월별 대여 건수를 조회합니다."
)
def get_rental_counts_by_date(
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency(allowed_roles=["master", "semi"]))
):
    counts = DashboardService.get_rental_counts_by_date(session)
    return RentalCountListResponse.success(message="Rental counts by month retrieved successfully", data=counts)

@router.get(
    "/sales/maintenance-cost",
    response_model=MaintenanceCostListResponse,
    summary="월별 정비 비용 조회",
    description="월별 정비 비용을 조회합니다."
)
def get_maintenance_cost_by_month(
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency(allowed_roles=["master", "semi"]))
):
    costs = DashboardService.get_maintenance_cost_by_month(session)
    return MaintenanceCostListResponse.success(message="Maintenance costs by month retrieved successfully", data=costs)

