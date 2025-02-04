from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from app.services.admin.rent_history_service import RentHistoryService
from app.core.database import get_session
from app.api.schemas.admin.rent_history_schema import RentHistoryResponse
from app.core.jwt import JWTPayload, jwt_handler

router = APIRouter()

@router.get(
    "/rent-history",
    response_model=RentHistoryResponse,
    summary="🚗 관리자 대여 로그 조회",
    description="관리자가 시스템에 등록된 모든 대여 로그 목록을 페이지네이션 방식으로 조회합니다.",
    responses={
        200: {
            "description": "✅ 대여 로그 조회 성공",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "Rent logs retrieved successfully",
                        "data": {
                            "rentHistory": [
                                {
                                    "rentId": 1,
                                    "userPk": 1,
                                    "vehicleNumber": "1234567890",
                                    "optionTypes": "옵션1,옵션2",
                                    "departureLocation": "위치1",
                                    "arrivalLocation": "위치2",
                                    "cost": 100000,
                                    "mileage": 10000,
                                    "status": "in_progress",
                                    "createdAt": "2024-01-01T00:00:00Z",
                                    "updatedAt": "2024-01-01T00:00:00Z"
                                }
                            ],
                            "pagination": {
                                "currentPage": 1,
                                "totalPages": 10,
                                "totalItems": 100,
                                "pageSize": 10
                            }
                        }
                    }
                }
            }
        },
        422: {
            "description": "유효성 검사 오류",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "FAILURE",
                        "message": "Validation error",
                        "error_code": "VALIDATION_ERROR",
                        "detail": {
                            "errors": [
                                {
                                    "loc": ["query", "page"],
                                    "msg": "ensure this value is greater than 0",
                                    "type": "value_error.number.not_gt",
                                    "ctx": {"limit_value": 0}
                                }
                            ]
                        },
                        "data": None
                    }
                }
            }
        },
        500: {
            "description": "서버 오류",
            "content": {
                "application/json": {
                    "examples": {
                        "DatabaseError": {
                            "summary": "데이터베이스 오류",
                            "value": {
                                "resultCode": "FAILURE",
                                "message": "Database error occurred",
                                "error_code": "DATABASE_ERROR",
                                "detail": {
                                    "error": "error message"
                                }
                            }
                        },
                        "InternalServerError": {
                            "summary": "예기치 못한 서버 오류 발생",
                            "value": {
                                "resultCode": "FAILURE",
                                "message": "Internal server error",
                                "error_code": "INTERNAL_SERVER_ERROR",
                                "detail": {
                                    "error": "error message"
                                }
                            }
                        }
                    }
                }
            }
        }
    }
)
async def get_rent_history(
    page: int = Query(1, description="현재 페이지 (최소 1)", gt=0),
    page_size: int = Query(10, description="페이지 크기 (최소 1)", gt=0),
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency(allowed_roles=["master", "semi"]))
):
    return RentHistoryService.get_rent_history(session, page, page_size)
