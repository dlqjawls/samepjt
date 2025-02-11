from typing import Annotated
from fastapi import APIRouter, Depends, Query, Path
from sqlmodel import Session
from app.core.database import get_session
from app.core.jwt import JWTPayload, jwt_handler
from app.services.admin.vehicle_service import VehicleService
from app.api.schemas.admin.vehicle_schema import VehicleCreate, VehiclesResponse, VehicleUpdateRequest, VehicleUpdateResponse, VehicleDeleteResponse

router = APIRouter()

@router.get(
    "/vehicles",
    response_model=VehiclesResponse,
    summary="🚗 차량 목록 조회",
    description="관리자가 등록된 차량 목록을 페이지네이션 방식으로 조회합니다.",
    responses={
        200: {
            "description": "차량 목록 조회 성공",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "Vehicle data retrieved successfully",
                        "data": {
                            "vehicles": [
                                {
                                    "vehicle_id": 1,
                                    "vin": "ABC123456789XYZ",
                                    "vehicle_number": "PBV-1234",
                                    "current_location": {"x": 12.313, "y": 32.3232},
                                    "mileage": 12000.5,
                                    "last_maintenance_at": "2025-01-10T12:00:00",
                                    "next_maintenance_at": "2025-06-10T12:00:00",
                                    "status": "Active",
                                    "created_at": "2024-05-01T08:30:00",
                                    "created_by": 3,
                                    "updated_at": "2025-01-10T12:00:00",
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
async def get_vehicle_list(
    page: int = Query(1, gt=0, description="현재 페이지 (최소 1)"),
    pageSize: int = Query(10, gt=0, description="페이지 당 차량 개수 (최소 1)"),
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency(allowed_roles=["semi", "master"]))
):
    return VehicleService.get_vehicle_list(session, page, pageSize)

@router.post(
    "/vehicles",
    response_model=VehiclesResponse,
    summary="🚗 차량 등록",
    description="차량 정보를 등록합니다.",
    responses={
        200: {
            "description": "차량이 성공적으로 등록됨",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "Vehicle registered successfully"
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
                        "detail": {
                            "error": "Authorization header is missing"
                        }
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
                        "error_code": "FORBIDDEN",
                        "detail": {
                            "role_required": "master",
                            "role_provided": "admin"
                        }
                    }
                }
            }
        },
        409: {
            "description": "차대번호 또는 차량 번호 중복",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "FAILURE",
                        "message": "Vehicle already exists",
                        "error_code": "CONFLICT",
                        "detail": {
                            "vin": "ABC123456789XYZ",
                            "error": "VIN already exists"
                        }
                    }
                }
            }
        },
        422: {
            "description": "유효하지 않은 입력값",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "FAILURE",
                        "message": "Validation error",
                        "error_code": "VALIDATION_ERROR",
                        "detail": {
                            "errors": [
                                {
                                    "field": "vin",
                                    "message": "VIN cannot be empty"
                                }
                            ]
                        }
                    }
                }
            }
        }
    }
)
async def create_vehicle(
    vehicle_data: VehicleCreate,
    session: Annotated[Session, Depends(get_session)],
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency(allowed_roles=["master"]))
) -> VehiclesResponse:
    return VehicleService.create_vehicle(session, vehicle_data, token_data.user_pk)

@router.patch(
    "/vehicles/{vehicle_id}",
    response_model=VehiclesResponse,
    summary="🚗 차량 수정",
    description="차량 정보를 수정합니다.",
    responses={
        200: {
            "description": "차량이 성공적으로 수정됨",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "Vehicle updated successfully"
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
                        "detail": {
                            "error": "Authorization header is missing"
                        }
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
                        "error_code": "FORBIDDEN",
                        "detail": {
                            "role_required": "master",
                            "role_provided": "admin"
                        }
                    }
                }
            }
        }
    }
)
async def update_vehicle(
    vehicle_data: VehicleUpdateRequest,
    vehicle_id: int = Path(..., description="차량 ID (최소 1)", gt=0),
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency(allowed_roles=["master"]))
) -> VehicleUpdateResponse:
    return VehicleService.update_vehicle(session = session, vehicle_data = vehicle_data, vehicle_id = vehicle_id, user_pk = token_data.user_pk)

@router.delete(
    "/vehicles/{vehicle_id}",
    response_model=VehicleDeleteResponse,
    summary="🚗 차량 삭제",
    description="차량 정보를 삭제합니다.",
    responses={
        200: {
            "description": "차량이 성공적으로 삭제됨",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "Vehicle deleted successfully"
                    }
                }
            }
        },
        400: {
            "description": "차량이 대여 중으로 삭제 불가",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "FAILURE",
                        "message": "Vehicle cannot be deleted while it is in use",
                        "error_code": "BAD_REQUEST",
                        "detail": {
                            "vehicle_id": 102,
                            "rent_status": "in-progress"
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
                        "detail": {
                            "error": "Authorization header is missing"
                        }
                    }
                }
            }
        },
        404: {
            "description": "차량이 존재하지 않음",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "FAILURE",
                        "message": "Vehicle not found",
                        "error_code": "NOT_FOUND",
                        "detail": {
                            "vehicle_id": 999
                        }
                    }
                }
            }
        }
    }
)
async def delete_vehicle(
    vehicle_id: int = Path(..., description="차량 ID (최소 1)", gt=0),
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency(allowed_roles=["master"]))
) -> VehicleDeleteResponse:
    return VehicleService.delete_vehicle(session, vehicle_id, token_data.user_pk)


