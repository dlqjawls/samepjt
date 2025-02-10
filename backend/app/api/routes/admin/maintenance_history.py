from fastapi import APIRouter, Depends, HTTPException, Path, Query, Body
from typing import Optional
from sqlmodel import Session
from app.core.database import get_session
from app.core.jwt import JWTPayload, jwt_handler
from app.services.admin.maintenance_history_service import MaintenanceHistoryService
from app.api.schemas.admin.maintenance_history_schema import (
    MaintenanceHistoryGetResponse,
    MaintenanceHistoryPostRequest,
    MaintenanceHistoryPostResponse,
    MaintenanceHistoryPatchRequest,
    MaintenanceHistoryPatchResponse,
    MaintenanceHistoryDeleteResponse
)

router = APIRouter()
  
@router.get(
    "/maintenance-history",
    response_model=MaintenanceHistoryGetResponse,
)
def get_maintenance_histories(
    item_type: Optional[str] = Query(None, description="아이템 유형 (vehicle, module, option)"),
    item_id: Optional[int] = Query(None, description="아이템 ID"),
    page: int = Query(1, description="페이지 번호", ge=1),
    pageSize: int = Query(10, description="한 페이지당 정비 기록 수", ge=1),
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency(allowed_roles=["master", "semi"]))
):
    return MaintenanceHistoryService.get_maintenance_history(
        session=session,
        itemType=item_type,
        itemId=item_id,
        page=page,
        pageSize=pageSize
    )


@router.post(
    "/maintenance-history",
    response_model=MaintenanceHistoryPostResponse,
)
def create_maintenance_history(
    payload: MaintenanceHistoryPostRequest,
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency(allowed_roles=["master"]))
):
    return MaintenanceHistoryService.create_maintenance_history(
        session=session,
        payload=payload,
        user_pk=token_data.user_pk
    )


@router.patch(
    "/maintenance-history/{maintenance_id}",
    response_model=MaintenanceHistoryPatchResponse,
)
def update_maintenance_history(
    maintenance_id: int = Path(..., description="정비 기록 ID"),
    payload: MaintenanceHistoryPatchRequest = Body(...),
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency(allowed_roles=["master"]))
):
    return MaintenanceHistoryService.update_maintenance_history(
        session=session,
        maintenance_id=maintenance_id,
        payload=payload,
        user_pk=token_data.user_pk
    )


@router.delete(
    "/maintenance-history/{maintenance_id}",
    response_model=MaintenanceHistoryDeleteResponse,
)
def delete_maintenance_history(
    maintenance_id: int = Path(..., description="정비 기록 ID"),
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency(allowed_roles=["master"]))
):
    return MaintenanceHistoryService.delete_maintenance_history(
        session=session,
        maintenance_id=maintenance_id,
        user_pk=token_data.user_pk
    )
