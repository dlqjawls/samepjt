from fastapi import APIRouter, Depends, Path, Query, Body
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
    summary="🎴 정비 기록 조회",
    description="관리자가 등록된 정비 기록 목록을 조회합니다. 아이템 유형(예: vehicle, module, option)과 아이템 ID로 필터링하며, 페이지네이션을 지원합니다.",
    responses={
        200: {
          "description": "정비 기록 조회 성공",
               "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "Maintenance history retrieved successfully",
                        "data": {
                            "maintenance_history": [
                                {
                                    "maintenance_id": 301,
                                    "item_id": 101,
                                    "item_type_name": "vehicle",
                                    "issue": "엔진 오일 교체 필요",
                                    "cost": 120.00,
                                    "maintenance_status_name": "pending",
                                    "scheduled_at": "2025-01-10T08:00:00",
                                    "completed_at": "2025-01-11T14:00:00",
                                    "created_at": "2025-01-05T10:00:00",
                                    "created_by": 3,
                                    "updated_at": "2025-01-11T14:00:00",
                                    "updated_by": 5
                                },
                                {
                                    "maintenance_id": 302,
                                    "item_id": 101,
                                    "item_type_name": "vehicle",
                                    "issue": "타이어 점검 필요",
                                    "cost": 50.00,
                                    "maintenance_status_name": "pending",
                                    "scheduled_at": "2025-02-01T10:00:00",
                                    "completed_at": None,
                                    "created_at": "2025-01-20T12:00:00",
                                    "created_by": 3,
                                    "updated_at": "2025-02-01T11:00:00",
                                    "updated_by": 5
                                }
                            ],
                            "pagination": {
                                "currentPage": 1,
                                "totalPages": 5,
                                "totalItems": 50,
                                "pageSize": 10
                            } 
                        }
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
                        "error_code": "UNAUTHORIZED",
                        "detail": {"error": "Authorization header is missing"}
                    }
                }
            }
        },
        422: {
            "description": "유효하지 않은 입력",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "FAILURE",
                        "message": "Validation error",
                        "error_code": "VALIDATION_ERROR",
                        "detail": {"errors": [{"field": "scheduled_at", "message": "Invalid date format"}]}
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
    summary="🎴 정비 기록 생성",
    description="새로운 정비 기록을 생성합니다. 요청 본문에 정비 대상 항목, 사유, 비용 및 예정 날짜 등의 정보를 포함합니다.",
    responses={
        200: {
            "description": "정비 기록 생성 성공",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "Maintenance history created successfully"
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
        403: {
            "description": "권한 없음",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "FAILURE",
                        "message": "Permission denied",
                        "error_code": "FORBIDDEN"
                    }
                }
            }
        },
        422: {
            "description": "유효하지 않은 입력",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "FAILURE",
                        "message": "Validation error",
                        "error_code": "VALIDATION_ERROR",
                        "detail": {"errors": [{"field": "scheduled_at", "message": "Invalid date format"}]}
                    }
                } 
            }
        } 
    }
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
    summary="🎴 정비 기록 수정",
    description="지정한 정비 기록 ID의 정비 기록을 수정합니다. 수정할 정보를 요청 본문에 포함하여 업데이트합니다.",
    responses={
        200: {
            "description": "정비 기록 수정 성공",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "Maintenance history updated successfully"
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
            "description": "정비 기록 없음",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "FAILURE",
                        "message": "Maintenance history not found",
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
    summary="🎴 정비 기록 삭제",
    description="지정한 정비 기록 ID의 정비 기록을 삭제합니다.",
    responses={
        200: {
            "description": "정비 기록 삭제 성공",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "Maintenance history deleted successfully"
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
            "description": "정비 기록 없음",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "FAILURE",
                        "message": "Maintenance history not found",
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
def delete_maintenance_history(
    maintenance_id: int = Path(..., description="정비 기록 ID", ge=1),
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency(allowed_roles=["master"]))
):
    return MaintenanceHistoryService.delete_maintenance_history(
        session=session,
        maintenance_id=maintenance_id,
        user_pk=token_data.user_pk
    )
