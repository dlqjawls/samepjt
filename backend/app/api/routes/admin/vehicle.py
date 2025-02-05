from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from app.core.database import get_session
from app.core.jwt import JWTPayload, jwt_handler
from app.services.admin.vehicle_service import VehicleService
from app.api.schemas.admin.vehicle_shema import VehiclesResponse

router = APIRouter()

@router.get(
    "/vehicles",
    response_model=VehiclesResponse,
    summary="🚗 관리자 차량 목록 조회",
    description="관리자가 등록된 차량 목록을 페이지네이션 방식으로 조회합니다.",
    responses={
        200: {
            "description": "✅ 차량 목록 조회 성공",
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
            "description": "❌ 인증 실패",
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
