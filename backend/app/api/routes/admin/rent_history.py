from fastapi import APIRouter, Depends, Query, Path
from sqlmodel import Session
from app.services.admin.rent_history_service import RentHistoryService 
from app.core.database import get_session
from app.api.schemas.admin.rent_history_schema import RentHistoryResponse, RentVideoResponse
from app.core.jwt import JWTPayload, jwt_handler

router = APIRouter()

@router.get(
    "/rent-history",
    response_model=RentHistoryResponse,
    summary="🚀 대여 로그 조회",
    description="관리자가 시스템에 등록된 모든 대여 로그 목록을 페이지네이션 방식으로 조회합니다.",
    responses={
        200: {
            "description": "대여 로그 조회 성공",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "Rent logs retrieved successfully",
                        "data": {
                            "rentHistory": [
                                {
                                    "rent_id": 1,
                                    "user_pk": 1,
                                    "vehicle_number": "PBV-00001",
                                    "option_types": "",
                                    "departure_location": {
                                      "x": 11.512,
                                      "y": 30.4531
                                    },
                                    "arrival_location": {
                                      "x": 12.313,
                                      "y": 32.3232
                                    },
                                    "cost": 500,
                                    "mileage": 0,
                                    "rent_status_name": "in_progress",
                                    "created_at": "2025-02-11T02:30:24.614775",
                                    "updated_at": "2025-02-11T02:30:24.614775"
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


@router.get(
    "/rent-history/{rent_id}/module-install-videos", 
    response_model=RentVideoResponse, 
    summary="🚀 모듈 설치 영상 조회",
    description="렌트 히스토리 모듈 설치 영상을 조회합니다.",
    responses={
        200: {
            "description": "모듈 설치 영상 조회 성공",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "Videos retrieved successfully",
                        "data": {
                            "videos": [
                                {
                                    "video_id": 501,
                                    "rent_id": 101,
                                    "video_type": "module installation",
                                    "video_url": "https://example.com/videos/501.mp4",
                                    "recorded_at": "2025-02-01T10:00:00"
                                } 
                            ]
                        }
                    }
                }
            }
        } 
    }
)
def get_module_install_videos(  
    session: Session = Depends(get_session),
    rent_id: int = Path(..., description="대여 ID"),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency(allowed_roles=["master", "semi"]))
):
    return RentHistoryService.get_rent_videos(session, rent_id, "module installation") 



@router.get(
    "/rent-history/{rent_id}/autonomous-videos", 
    response_model=RentVideoResponse, 
    summary="🚀 자율주행 영상 조회",
    description="렌트 히스토리 자율주행 영상을 조회합니다.",
    responses={
        200: {
            "description": "자율주행 영상 조회 성공",
              "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "Videos retrieved successfully",
                        "data": {
                            "videos": [
                                {
                                    "video_id": 502,
                                    "rent_id": 101,
                                    "video_type": "autonomous driving",
                                    "video_url": "https://example.com/videos/502.mp4",
                                    "recorded_at": "2025-02-01T10:00:00"
                                }
                            ]
                        }
                    }
                }
            }
        }
    }
)
def get_autonomous_videos(
    session: Session = Depends(get_session),
    rent_id: int = Path(..., description="대여 ID"),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency(allowed_roles=["master", "semi"]))
):
    return RentHistoryService.get_rent_videos(session, rent_id, "autonomous driving") 