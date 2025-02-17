from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.core.database import get_session
from app.core.jwt import JWTPayload, jwt_handler
from app.services.user.me_service import MeRentInfoService
from app.api.schemas.user.me_schema import MeRentInfoResponse, MeRentHistoryResponse

router = APIRouter()


@router.get(
    "/me/rent/current",
    response_model=MeRentInfoResponse,
    summary="👀 현재 진행 중인 렌트 정보 조회",
    description="JWT 토큰으로 인증된 현재 사용자의 진행 중인 렌트 정보를 조회합니다.",
    responses={
        200: {
            "description": "현재 진행 중인 렌트 정보 조회 성공",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "Current rent info retrieved successfully",
                        "data": {
                            "rent_id": 1,
                            "rentStartDate": "2025-01-15T09:00:00",
                            "rentEndDate": "2025-01-15T10:00:00",
                            "cost": 100000
                        }
                    }
                }
            }
        },
        404: {
            "description": "진행 중인 렌트 정보가 존재하지 않는 경우",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "FAILURE",
                        "message": "진행중인 렌트 정보가 존재하지 않습니다.",
                        "error_code": "NOT_FOUND",
                        "detail": {
                            "user_pk": 123
                        }
                    }
                }
            }
        },
        500: {
            "description": "렌트 정보가 존재하지 않는 경우",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "FAILURE",
                        "message": "렌트 정보가 존재하지 않습니다.",
                        "error_code": "DATABASE_ERROR",
                        "detail": {
                            "rent_id": 123
                        }
                    }
                }
            }
        }
    }
)
async def get_current_rent_info(
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency())
):
    return MeRentInfoService.get_current_rent_info(session, token_data.user_pk)
    
@router.get(
    "/me/rent/history",
    response_model=MeRentHistoryResponse,
    summary="👀 렌트 이력 조회",
    description="JWT 토큰으로 인증된 사용자의 렌트 이력을 조회합니다.",
    responses={
        200: {
            "description": "렌트 이력 조회 성공",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "Rent history retrieved successfully",
                        "data": [
                            {
                                "rent_id": 1,
                                "rentStartDate": "2025-01-15T09:00:00",
                                "rentEndDate": "2025-01-15T10:00:00",
                                "cost": 100000
                            },
                            {
                                "rent_id": 2,
                                "rentStartDate": "2025-02-01T09:00:00",
                                "rentEndDate": "2025-02-01T11:00:00",
                                "cost": 200000
                            }
                        ]
                    }
                }
            }
        }
    }
)
async def get_rent_history(
    session: Session = Depends(get_session),  
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency())
):
    return MeRentInfoService.get_rent_history(session, token_data.user_pk)
    
