from typing import Annotated
from fastapi import APIRouter, Depends, Query, Path, HTTPException
from sqlmodel import Session
from app.core.database import get_session
from app.core.jwt import JWTPayload, jwt_handler
from app.services.admin.option_type_service import OptionTypeService
from app.api.schemas.admin.option_type_schema import OptionTypeGetResponse, OptionTypeRegisterRequest, OptionTypeRegisterResponse, OptionTypeUpdateRequest, OptionTypeUpdateResponse, OptionTypeDeleteResponse

router = APIRouter()

@router.get(
    "/option-types",
    response_model=OptionTypeGetResponse,
    summary="🚗 관리자 옵션 타입 목록 조회",
    description="관리자가 등록된 옵션 타입 목록을 페이지네이션 방식으로 조회합니다.",
    responses={
        200: {
            "description": "✅ 옵션 타입 목록 조회 성공",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "Option type data retrieved successfully",
                        "data": {
                            "option_types": [
                                {
                                    "option_type_id": 1,
                                    "option_type_name": "Option Type 1",
                                    "option_type_description": "Option Type 1 Description",
                                    "option_type_status": "Active",
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
async def get_option_type_list(
    page: int = Query(1, gt=0, description="현재 페이지 (최소 1)"),
    pageSize: int = Query(10, gt=0, description="페이지 당 옵션 타입 개수 (최소 1)"),
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency(allowed_roles=["semi", "master"]))
):
    return OptionTypeService.get_option_type_list(session, page, pageSize)

@router.post(
    "/option-types",
    response_model=OptionTypeRegisterResponse,
    status_code=201,
    responses={
        201: {
            "description": "옵션 타입이 성공적으로 등록됨",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "Option type registered successfully"
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
            "description": "옵션 타입 이름 중복",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "FAILURE",
                        "message": "Option type already exists",
                        "error_code": "CONFLICT",
                        "detail": {
                            "option_type_name": "Option Type 1",
                            "error": "Option type name already exists"
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
                                    "field": "option_type_name",
                                    "message": "Option type name cannot be empty"
                                }
                            ]
                        }
                    }
                }
            }
        }
    }
)
async def create_option_type(
    option_type_data: OptionTypeRegisterRequest,
    session: Annotated[Session, Depends(get_session)],
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency(allowed_roles=["master"]))
) -> OptionTypeRegisterResponse:
    """
    옵션 타입 등록 API

    Args:
    - option_type_data: 옵션 타입 등록 정보
        - option_type_name (str): 옵션 타입 이름
        - option_type_description (str): 옵션 타입 설명

    Returns:
    - OptionTypesResponse: 옵션 타입 등록 결과
        - resultCode (str): 처리 결과 코드
        - message (str): 처리 결과 메시지

    Raises:
    - 401 UNAUTHORIZED: 인증 실패
    - 403 FORBIDDEN: 권한 없음 (master 권한 필요)
    - 409 CONFLICT: 옵션 타입 이름 중복
    - 422 VALIDATION_ERROR: 유효하지 않은 입력값
    """
    return OptionTypeService.register_option_type(session, option_type_data, token_data.user_pk)

@router.patch(
    "/option-types/{option_type_id}",
    response_model=OptionTypeUpdateResponse,
    responses={
        200: {
            "description": "옵션 타입가 성공적으로 수정됨",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "Option type updated successfully"
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
async def update_option_type(  
    option_type_data: OptionTypeUpdateRequest,
    option_type_id: int = Path(..., description="🚗 옵션 타입 ID (최소 1)", gt=0),
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency(allowed_roles=["master"]))
) -> OptionTypeUpdateResponse:
    """
    옵션 타입 수정 API

    Args:
    - option_type_data: 옵션 타입 수정 정보
        - option_type_name (str): 옵션 타입 이름
        - option_type_description (str): 옵션 타입 설명
        - option_type_images (List[str]): 옵션 타입 이미지
        - option_type_features (str): 옵션 타입 특징
        - option_type_size (str): 옵션 타입 크기
        - option_type_cost (float): 옵션 타입 가격

    Returns:
    - OptionTypeUpdateResponse: 옵션 타입 수정 결과
        - resultCode (str): 처리 결과 코드
        - message (str): 처리 결과 메시지

    Raises:
    - 401 UNAUTHORIZED: 인증 실패
    - 403 FORBIDDEN: 권한 없음 (master 권한 필요)
    - 409 CONFLICT: 옵션 타입 이름 중복
    - 422 VALIDATION_ERROR: 유효하지 않은 입력값
    """
    return OptionTypeService.update_option_type(
        session=session,
        option_type_id=option_type_id,
        update_data=option_type_data,
        user_pk=token_data.user_pk
    )

@router.delete(
    "/option-types/{option_type_id}",
    response_model=OptionTypeDeleteResponse,
    responses={
        200: {
            "description": "옵션 타입가 성공적으로 삭제됨",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "Option type deleted successfully"
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
            "description": "옵션 타입가 존재하지 않음",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "FAILURE",
                        "message": "Option type not found",
                        "error_code": "NOT_FOUND",
                        "detail": {
                            "option_type_id": 999
                        }
                    }
                }
            }
        }
    }
)
async def delete_option_type(
    option_type_id: int = Path(..., description="🚗 옵션 타입 ID (최소 1)", gt=0),
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency(allowed_roles=["master"]))
) -> OptionTypeDeleteResponse:
    """
    옵션 타입 삭제 API

    Args:
    - option_type_id: 삭제할 옵션 타입의 고유 ID

    Returns:
    - OptionTypeDeleteResponse: 옵션 타입 삭제 결과
        - resultCode (str): 처리 결과 코드
        - message (str): 처리 결과 메시지

    Raises:
    - 401 UNAUTHORIZED: 인증 실패
    - 404 NOT_FOUND: 존재하지 않는 옵션 타입 ID
    """
    return OptionTypeService.delete_option_type(session, option_type_id, token_data.user_pk)


