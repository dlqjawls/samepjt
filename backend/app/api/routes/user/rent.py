from fastapi import APIRouter, Depends, Path
from sqlmodel import Session
from app.core.database import get_session
from app.services.user.rent_service import RentService
from app.api.schemas.user import rent_schema
from app.core.jwt import JWTPayload, jwt_handler

router = APIRouter()

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
    description="""
    사용자가 **진행 중인 렌트 요청을 취소**하는 API입니다.
    
    **취소 절차:**
    1. 렌트 상태를 `CANCELED`(취소됨)으로 변경
    2. 관련 차량/모듈/옵션 상태를 `INACTIVE`로 변경
    3. 사용 기록 상태 업데이트
    
    **주의사항:**
    - 취소된 렌트는 다시 활성화할 수 없습니다
    - 본인의 렌트만 취소할 수 있습니다
    - 이미 취소되었거나 완료된 렌트는 취소할 수 없습니다
    """,
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
