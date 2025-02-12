from fastapi import APIRouter, Depends, Path, Query
from sqlmodel import Session
from app.core.database import get_session
from app.services.user.rent_service import RentService
from app.api.schemas.user import rent_schema
from app.core.jwt import JWTPayload, jwt_handler
from datetime import date

router = APIRouter()

@router.get(
    "/rent/{rent_id}",
    response_model=rent_schema.RentStatusResponse,
    summary="🚀 렌트 차량 상태 조회",
    description="사용자가 **진행 중인 렌트 차량 상태를 조회**하는 API입니다.",
    responses={
        200: {
            "description": "차량 상태 조회 성공",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "Vehicle rent status retrieved successfully",
                        "data": {
                            "isArrive": False,
                            "location": {"x": 12.313, "y": 32.3232},
                            "destination": {"x": 40.1111, "y": 100.4194},
                            "ETA": "2025-01-13T14:30:00Z",
                            "distanceTravelled": 120.0,
                            "plannedPath": [
                                {"x": 12.3200, "y": 32.3300},
                                {"x": 15.4500, "y": 35.6000}
                            ],
                            "SLAMMapData": "base64-encoded-map-data",
                            "status": {
                                "vehicle": {
                                    "batteryLevel": 85,
                                    "lightBrightness": 80
                                },
                                "options": [
                                    {
                                        "optionName": "물탱크",
                                        "optionStatus": "잔여량: 50L"
                                    },
                                    {
                                        "optionName": "배터리 팩",
                                        "optionStatus": "잔여량: 80%"
                                    }
                                ]
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
                        "message": "You do not have permission to access this rent",
                        "error_code": "FORBIDDEN"
                    }
                }
            }
        },
        404: {
            "description": "렌트 기록 없음",
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
            "description": "상태 충돌",
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
    rent_id: int = Path(..., description="조회할 렌트 ID (1 이상)", gt=0),
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency())
) -> rent_schema.RentStatusResponse:
    return RentService.get_rent_status(session, rent_id, token_data.user_pk)
  
@router.post(
    "/rent",
    response_model=rent_schema.RentResponse,
    summary="🚀 렌트 요청",
    description="사용자가 차량, 모듈, 옵션을 선택하여 **렌트 요청**을 생성합니다.",
    responses={
        200: {
            "description": "렌트 요청 성공",
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
        400: {
            "description": "잘못된 요청",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "FAILURE",
                        "message": "Invalid request",
                        "error_code": "BAD_REQUEST",
                        "detail": {
                            "module_type_cost": 10000,
                            "option_cost": 10000,
                            "date_cost": 10000,
                            "total_cost": 30000
                        }
                    }
                }
            }
        },
        404: {
            "description": "리소스를 찾을 수 없음",
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
    summary="🚀 렌트 취소",
    description="사용자가 **진행 중인 렌트 요청을 취소**하는 API입니다.",
    response_model=rent_schema.CancelRentResponse,
    responses={
        200: {
            "description": "렌트 취소 성공",
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
            "description": "인증 실패",
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
            "description": "권한 없음",
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
            "description": "렌트 기록 없음",
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
            "description": "상태 충돌",
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
            "description": "유효성 검사 실패",
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
            "description": "서버 오류",
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
async def cancel_rent(
    rent_id: int = Path(..., description="렌트 ID (최소 1)", gt=0),
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency())
):
    rent_result = RentService.cancel_rent(session, rent_id, token_data.user_pk)
    return rent_result

@router.post(
    "/rent/{rent_id}/complete",
    response_model=rent_schema.CompleteRentResponse,
    summary="🚀 렌트 완료",
    description="사용자가 **진행 중인 렌트를 완료**하는 API입니다.",
    responses={
        200: {
            "description": "렌트 완료 성공",
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
            "description": "권한 없음",
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
            "description": "렌트 기록 없음",
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
            "description": "상태 충돌",
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
    rent_id: int = Path(..., description="완료할 렌트 ID (최소 1)", gt=0),
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency())
) -> rent_schema.CompleteRentResponse:
    return RentService.complete_rent(session, rent_id, token_data.user_pk)




# 기간별 렌트 비용 계산
@router.post(
    "/rent/calculate-duration-cost",
    summary="🚀 기간별 렌트 비용 계산",
    description="사용자가 **기간별 렌트 비용을 계산**하는 API입니다.",
    response_model=rent_schema.RentCostResponse,
) 
async def get_rent_cost(
    rent_request: rent_schema.RentCostRequest,  
) -> rent_schema.RentCostResponse:
    cost = RentService.calculate_rental_cost(rent_request.rentStartDate, rent_request.rentEndDate) 
    rent_cost_data = rent_schema.RentCostResponseData(cost=cost)
    return rent_schema.RentCostResponse.success(message="Rental cost calculated successfully", data=rent_cost_data)
