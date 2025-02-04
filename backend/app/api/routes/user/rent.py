from fastapi import APIRouter, Depends, Path
from sqlmodel import Session
from app.core.database import get_session
from app.services.user.rent_service import RentService
from app.api.schemas.user import rent_schema
from app.core.jwt import JWTPayload, jwt_handler

router = APIRouter()

@router.get(
    "/rent/{rent_id}",
    response_model=rent_schema.RentStatusResponse,
    summary="🚗 차량 렌트 상태 조회",
    description="사용자가 **진행 중인 차량 렌트 상태를 조회**하는 API입니다.",
    responses={
        200: {
            "description": "✅ 차량 상태 조회 성공",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "Rent status retrieved successfully",
                        "data": {
                            "rent_id": 123,
                            "vehicle_number": "서울 12가 3456",
                            "current_status": "in_progress",
                            "current_location": { "lat": 37.5665, "lng": 126.9780 },
                            "destination": { "lat": 37.579617, "lng": 126.977041 },
                            "route_path": [
                                { "lat": 37.5665, "lng": 126.9780 },
                                { "lat": 37.5701, "lng": 126.9795 },
                                { "lat": 37.5745, "lng": 126.9813 }
                            ]
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
                        "error_code": "UNAUTHORIZED"
                    }
                }
            }
        },
        403: {
            "description": "🚫 권한 없음",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "FAILURE",
                        "message": "You do not have permission to access this rent",
                        "error_code": "FORBIDDEN"
                    }
                }
            }
        },
        404: {
            "description": "❓ 렌트 기록 없음",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "FAILURE",
                        "message": "Rent not found",
                        "error_code": "NOT_FOUND",
                        "detail": {
                            "rent_id": 123
                        }
                    }
                }
            }
        },
        409: {
            "description": "⚠️ 상태 충돌",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "FAILURE",
                        "message": "Rent has already been completed or canceled",
                        "error_code": "CONFLICT",
                        "detail": {
                            "rent_id": 123,
                            "current_status": "completed"
                        }
                    }
                }
            }
        }
    }
)
async def get_rent_status(
    rent_id: int = Path(..., description="🔍 조회할 렌트 ID (1 이상)", gt=0),
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency())
) -> rent_schema.RentStatusResponse:
    """차량 렌트 상태 조회 엔드포인트"""
    return RentService.get_rent_status(session, rent_id, token_data.user_pk)
  
@router.post(
    "/rent",
    response_model=rent_schema.RentResponse,
    summary="🚗 렌트 요청",
    description="사용자가 차량, 모듈, 옵션을 선택하여 **렌트 요청**을 생성합니다.",
    responses={
        200: {
            "description": "✅ 렌트 요청 성공",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "Rent created successfully",
                        "data": {
                            "rent_id": 123,
                            "vehicle_number": "서울 12가 3456"
                        }
                    }
                }
            }
        },
        404: {
            "description": "❌ 리소스를 찾을 수 없음",
            "content": {
                "application/json": {
                    "examples": {
                        "NoAvailableVehicle": {
                            "summary": "사용 가능한 차량 없음",
                            "value": {
                                "resultCode": "FAILURE",
                                "message": "No available vehicle found",
                                "error_code": "NOT_FOUND",
                                "detail": {
                                    "error": "모든 차량이 사용 중입니다."
                                }
                            }
                        },
                        "NoAvailableModule": {
                            "summary": "사용 가능한 모듈 없음", 
                            "value": {
                                "resultCode": "FAILURE",
                                "message": "No available module found",
                                "error_code": "NOT_FOUND",
                                "detail": {
                                    "error": "모든 모듈이 사용 중입니다."
                                }
                            }
                        },
                        "NotEnoughOptions": {
                            "summary": "옵션 수량 부족",
                            "value": {
                                "resultCode": "FAILURE", 
                                "message": "Not enough available options",
                                "error_code": "NOT_FOUND",
                                "detail": {
                                    "option_type_id": 1,
                                    "required": 2,
                                    "available": 1
                                }
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
                                    "loc": ["body", "selectedOptionTypes"],
                                    "msg": "No options selected",
                                    "type": "value_error",
                                }
                            ]
                        }
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
                        "message": "Failed to create rent",
                        "error_code": "DATABASE_ERROR",
                        "detail": {
                            "error": "Database transaction failed"
                        }
                    }
                }
            }
        }
    }
)
async def rent_vehicle(
    rent_request: rent_schema.RentRequest,
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency())
):
    rent_result = RentService.create_rent(session, rent_request, token_data.user_pk)
    return rent_result


@router.delete(
    "/rent/{rent_id}",
    summary="🚗 렌트 취소",
    description="사용자가 **진행 중인 렌트 요청을 취소**하는 API입니다.",
    response_model=rent_schema.CancelRentResponse,
    responses={
        200: {
            "description": "✅ 렌트 취소 성공",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "Rent canceled successfully",
                        "data": {
                            "rent_id": 123
                        }
                    }
                }
            }
        },
        401: {
            "description": "❌ 인증 실패",
            "content": {
                "application/json": {
                    "examples": {
                        "ExpiredToken": {
                            "summary": "토큰 만료",
                            "value": {
                                "resultCode": "FAILURE",
                                "message": "Token has expired",
                                "error_code": "UNAUTHORIZED",
                                "detail": {
                                    "error": "Token expiration time has passed"
                                }
                            }
                        }
                    }
                }
            }
        },
        403: {
            "description": "🚫 권한 없음",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "FAILURE",
                        "message": "Permission denied",
                        "error_code": "FORBIDDEN",
                        "detail": {
                            "rent_id": 123,
                            "request_user": 456,
                            "rent_user": 789
                        }
                    }
                }
            }
        },
        404: {
            "description": "❓ 렌트 기록 없음",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "FAILURE",
                        "message": "Rent history not found",
                        "error_code": "NOT_FOUND",
                        "detail": {
                            "rent_id": 123
                        }
                    }
                }
            }
        },
        409: {
            "description": "⚠️ 상태 충돌",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "FAILURE",
                        "message": "Rent already canceled or completed",
                        "error_code": "CONFLICT",
                        "detail": {
                            "rent_id": 123,
                            "current_status": 3
                        }
                    }
                }
            }
        },
        422: {
            "description": "❌ 유효성 검사 실패",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "FAILURE",
                        "message": "Validation error",
                        "error_code": "VALIDATION_ERROR",
                        "detail": {
                            "errors": [{
                                "loc": ["path", "rent_id"],
                                "msg": "rent_id must be a positive integer",
                                "type": "value_error"
                            }]
                        }
                    }
                }
            }
        },
        500: {
            "description": "⚠️ 서버 오류",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "FAILURE",
                        "message": "Failed to cancel rent",
                        "error_code": "DATABASE_ERROR",
                        "detail": {
                            "error": "Database transaction failed",
                            "rent_id": 123
                        }
                    }
                }
            }
        }
    }
)
async def soft_delete_rent(
    rent_id: int = Path(..., description="🔍 렌트 ID (최소 1)", gt=0),
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency())
):
    rent_result = RentService.cancel_rent(session, rent_id, token_data.user_pk)
    return rent_result

@router.post(
    "/rent/{rent_id}/complete",
    response_model=rent_schema.CompleteRentResponse,
    summary="🚗 렌트 완료",
    description="사용자가 **진행 중인 렌트를 완료**하는 API입니다.",
    responses={
        200: {
            "description": "✅ 렌트 완료 성공",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "Rental completed successfully",
                        "data": {
                            "rent_id": 123,
                            "total_mileage": 150.0,
                            "usage_duration": 3,
                            "estimated_payback_amount": 75000
                        }
                    }
                }
            }
        },
        403: {
            "description": "🚫 권한 없음",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "FAILURE",
                        "message": "Permission denied",
                        "error_code": "FORBIDDEN",
                        "detail": {
                            "rent_id": 123,
                            "request_user": 3,
                            "rent_user": 5
                        }
                    }
                }
            }
        },
        404: {
            "description": "❓ 렌트 기록 없음",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "FAILURE",
                        "message": "Rent history not found",
                        "error_code": "NOT_FOUND",
                        "detail": {
                            "rent_id": 123
                        }
                    }
                }
            }
        },
        409: {
            "description": "⚠️ 상태 충돌",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "FAILURE",
                        "message": "Rent already completed or canceled",
                        "error_code": "CONFLICT",
                        "detail": {
                            "rent_id": 123,
                            "current_status": "COMPLETED"
                        }
                    }
                }
            }
        }
    }
)
async def complete_rent(
    rent_id: int = Path(..., description="🔍 완료할 렌트 ID (최소 1)", gt=0),
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency())
) -> rent_schema.CompleteRentResponse:
    """렌트 완료 엔드포인트"""
    return RentService.complete_rent(session, rent_id, token_data.user_pk)

