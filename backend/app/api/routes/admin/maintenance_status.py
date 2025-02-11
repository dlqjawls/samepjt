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
    summary="🎳 정비 기록 상태 조회",
    description="관리자가 등록된 정비 기록 상태 목록을 조회합니다.",
    responses={
        200: {
            "description": "정비 기록 상태 목록 조회 성공",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "Maintenance statuses retrieved successfully",
                        "data": {"maintenance_statuses": [
                            {"maintenance_status_id": 1, "maintenance_status_name": "pending"},
                            {"maintenance_status_id": 2, "maintenance_status_name": "in_progress"},
                            {"maintenance_status_id": 3, "maintenance_status_name": "completed"}
                        ]}
                    }
                }
            }
        },
        401: {
            "description": "인증 실패",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "FAILURE",
                        "message": "Authentication required",
                        "error_code": "UNAUTHORIZED"
                    }
                }
            }
        },
        404: {
            "description": "정비 기록 상태 목록 조회 실패",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "FAILURE",
                        "message": "Maintenance statuses retrieval failed",
                        "error_code": "NOT_FOUND"
                    }
                }
            }
        },
        500: {
            "description": "서버 오류",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "FAILURE",
                        "message": "An internal error occurred",
                        "error_code": "INTERNAL_SERVER_ERROR"
                    }
                }
            }
        }
    }
)
def get_maintenance_statuses(
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency(allowed_roles=["semi", "master"]))
):
    return MaintenanceStatusService.get_maintenance_statuses(session) 