from typing import Annotated
from fastapi import APIRouter, Depends, Query, Path, UploadFile, File
from sqlmodel import Session
from app.core.database import get_session
from app.core.jwt import JWTPayload, jwt_handler
from app.services.admin.option_type_service import OptionTypeService
from app.api.schemas.admin.option_type_schema import OptionTypeGetResponse, OptionTypeRegisterRequest, OptionTypeMessageResponse, OptionTypeRemoveImageRequest, OptionTypeUpdateRequest

router = APIRouter()

@router.get(
    "/option-types",
    response_model=OptionTypeGetResponse,
    summary="🛠️ 옵션 타입 목록 조회",
    description="등록된 옵션 타입 목록을 페이지네이션 방식으로 조회합니다.",
    responses={
        200: {
            "description": "옵션 타입 목록 조회 성공",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "Option type data retrieved successfully",
                        "data": {
                            "option_types": [
                                {
                                    "option_type_id": 1,
                                    "option_type_name": "배터리 팩",
                                    "description": "중형 배터리 팩 (리튬이온)",
                                    "option_type_images": ["https://example.com/images/option-type-1.jpg"],
                                    "option_type_features": "긴 배터리 수명, 빠른 충전",
                                    "option_type_size": "Medium",
                                    "option_type_cost": 500.00,
                                    "created_at": "2025-01-10T12:00:00",
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
async def get_option_type_list(
    page: int = Query(1, gt=0, description="현재 페이지 (최소 1)"),
    pageSize: int = Query(10, gt=0, description="페이지 당 옵션 타입 개수 (최소 1)"),
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency(allowed_roles=["semi", "master"]))
):
    return OptionTypeService.get_option_type_list(session, page, pageSize)

@router.post(
    "/option-types",
    response_model=OptionTypeMessageResponse,
    summary="🛠️ 옵션 타입 등록",
    description="새로운 옵션 타입을 등록하는 API입니다.",
    responses={
        200: {
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
) -> OptionTypeMessageResponse:
    return OptionTypeService.register_option_type(session, option_type_data, token_data.user_pk)

@router.patch(
    "/option-types/{option_type_id}",
    response_model=OptionTypeMessageResponse,
    summary="🛠️ 옵션 타입 수정",
    description="기존 옵션 타입을 수정하는 API입니다.",
    responses={
        200: {
            "description": "옵션 타입 수정 성공",
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
    option_type_id: int = Path(..., description="옵션 타입 ID (최소 1)", gt=0),
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency(allowed_roles=["master"]))
) -> OptionTypeMessageResponse:
    return OptionTypeService.update_option_type(
        session=session,
        option_type_id=option_type_id,
        option_type_data=option_type_data,
        user_pk=token_data.user_pk
    )

@router.delete(
    "/option-types/{option_type_id}",
    response_model=OptionTypeMessageResponse,
    summary="🛠️ 옵션 타입 삭제",
    description="기존 옵션 타입을 삭제하는 API입니다.",
    responses={
        200: {
            "description": "옵션 타입 삭제 성공",
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
            "description": "옵션 타입 존재하지 않음",
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
    option_type_id: int = Path(..., description="옵션 타입 ID (최소 1)", gt=0),
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency(allowed_roles=["master"]))
) -> OptionTypeMessageResponse:
    return OptionTypeService.delete_option_type(session, option_type_id, token_data.user_pk)



@router.post(
    "/option-types/{option_type_id}/images",
    response_model=OptionTypeMessageResponse,
    summary="🛠️ 옵션 타입 이미지 추가",
    description="옵션 타입에 이미지를 추가하는 API입니다.",
    responses={
        200: {
            "description": "옵션 타입 이미지 추가 성공",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "Option type image added successfully"
                    }
                }
            }
        }
    }
)
async def add_option_type_image(
    option_type_id: int = Path(..., description="옵션 타입 ID (최소 1)", gt=0),
    images: UploadFile = File(...),
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency(allowed_roles=["master"]))
) -> OptionTypeMessageResponse:
    return OptionTypeService.add_option_type_image(session, option_type_id, images)    

@router.delete(
    "/option-types/{option_type_id}/images",
    response_model=OptionTypeMessageResponse,  
    summary="🛠️ 옵션 타입 이미지 삭제",
    description="옵션 타입에 이미지를 삭제하는 API입니다.",
    responses={
        200: {
            "description": "옵션 타입 이미지 삭제 성공",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "Option type image removed successfully"  
                    }
                }
            }
        }
    }
)
async def remove_option_type_image(  
    request: OptionTypeRemoveImageRequest,
    option_type_id: int = Path(..., description="옵션 타입 ID (최소 1)", gt=0),
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency(allowed_roles=["master"]))
) -> OptionTypeMessageResponse:
    return OptionTypeService.remove_option_type_image(session, option_type_id, request)      
  