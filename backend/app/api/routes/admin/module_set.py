from typing import Annotated
from fastapi import APIRouter, Depends, Query, Path, HTTPException
from sqlmodel import Session
from app.core.database import get_session
from app.core.jwt import JWTPayload, jwt_handler
from app.services.admin.module_set_service import ModuleSetService
from app.api.schemas.admin.module_set_schema import ModuleSetGetResponse, ModuleSetRegisterRequest, ModuleSetRegisterResponse, ModuleSetUpdateRequest, ModuleSetUpdateResponse, ModuleSetDeleteResponse

router = APIRouter()

@router.get(
    "/module-sets",
    response_model=ModuleSetGetResponse,
    summary="🚗 관리자 모듈 세트 목록 조회",
    description="관리자가 등록된 모듈 세트 목록을 페이지네이션 방식으로 조회합니다.",
    responses={
        200: {
            "description": "✅ 모듈 세트 목록 조회 성공",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "Module set data retrieved successfully",
                        "data": {
                            "module_sets": [
                                {
                                    "module_set_id": 1,
                                    "module_set_name": "Module Set 1",
                                    "module_set_description": "Module Set 1 Description",
                                    "module_set_status": "Active",
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
async def get_module_set_list(
    page: int = Query(1, gt=0, description="현재 페이지 (최소 1)"),
    pageSize: int = Query(10, gt=0, description="페이지 당 모듈 세트 개수 (최소 1)"),
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency(allowed_roles=["semi", "master"]))
):
    return ModuleSetService.get_module_set_list(session, page, pageSize)

@router.post(
    "/module-sets",
    response_model=ModuleSetRegisterResponse,
    status_code=201,
    responses={
        201: {
            "description": "모듈 세트가 성공적으로 등록됨",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "Module set registered successfully"
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
            "description": "모듈 세트 이름 중복",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "FAILURE",
                        "message": "Module set already exists",
                        "error_code": "CONFLICT",
                        "detail": {
                            "module_set_name": "Module Set 1",
                            "error": "Module set name already exists"
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
                                    "field": "module_set_name",
                                    "message": "Module set name cannot be empty"
                                }
                            ]
                        }
                    }
                }
            }
        }
    }
)
async def create_module_set(
    module_set_data: ModuleSetRegisterRequest,
    session: Annotated[Session, Depends(get_session)],
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency(allowed_roles=["master"]))
) -> ModuleSetRegisterResponse:
    """
    모듈 세트 등록 API

    Args:
    - module_set_data: 모듈 세트 등록 정보
        - module_set_name (str): 모듈 세트 이름
        - module_set_description (str): 모듈 세트 설명
        - module_set_images (List[str]): 모듈 세트 이미지
        - module_set_features (str): 모듈 세트 특징
        - module_type_id (int): 모듈 타입 ID

    Returns:
    - ModuleSetsResponse: 모듈 세트 등록 결과
        - resultCode (str): 처리 결과 코드
        - message (str): 처리 결과 메시지

    Raises:
    - 401 UNAUTHORIZED: 인증 실패
    - 403 FORBIDDEN: 권한 없음 (master 권한 필요)
    - 409 CONFLICT: 모듈 세트 이름 중복
    - 422 VALIDATION_ERROR: 유효하지 않은 입력값
    """
    return ModuleSetService.register_module_set(session, module_set_data, token_data.user_pk)

@router.patch(
    "/module-sets/{module_set_id}",
    response_model=ModuleSetUpdateResponse,
    responses={
        200: {
            "description": "모듈 세트가 성공적으로 수정됨",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "Module set updated successfully"
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
async def update_module_set(
    module_set_data: ModuleSetUpdateRequest,
    module_set_id: int = Path(..., description="🚗 모듈 세트 ID (최소 1)", gt=0),
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency(allowed_roles=["master"]))
) -> ModuleSetUpdateResponse:
    """
    모듈 세트 수정 API

    Args:
    - module_set_data: 모듈 세트 수정 정보
        - module_set_name (str): 모듈 세트 이름
        - module_set_description (str): 모듈 세트 설명
        - module_set_images (List[str]): 모듈 세트 이미지
        - module_set_features (str): 모듈 세트 특징
        - module_type_id (int): 모듈 타입 ID

    Returns:
    - ModuleSetUpdateResponse: 모듈 세트 수정 결과
        - resultCode (str): 처리 결과 코드
        - message (str): 처리 결과 메시지

    Raises:
    - 401 UNAUTHORIZED: 인증 실패
    - 403 FORBIDDEN: 권한 없음 (master 권한 필요)
    - 409 CONFLICT: 모듈 세트 이름 중복
    - 422 VALIDATION_ERROR: 유효하지 않은 입력값
    """
    return ModuleSetService.update_module_set(
        session=session,
        module_set_id=module_set_id,
        update_data=module_set_data,
        user_pk=token_data.user_pk
    )

@router.delete(
    "/module-sets/{module_set_id}",
    response_model=ModuleSetDeleteResponse,
    responses={
        200: {
            "description": "모듈 세트가 성공적으로 삭제됨",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "Module set deleted successfully"
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
            "description": "모듈 세트가 존재하지 않음",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "FAILURE",
                        "message": "Module set not found",
                        "error_code": "NOT_FOUND",
                        "detail": {
                            "module_set_id": 999
                        }
                    }
                }
            }
        }
    }
)
async def delete_module_set(
    module_set_id: int = Path(..., description="🚗 모듈 세트 ID (최소 1)", gt=0),
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency(allowed_roles=["master"]))
) -> ModuleSetDeleteResponse:
    """
    모듈 세트 삭제 API

    Args:
    - module_set_id: 삭제할 모듈 세트의 고유 ID

    Returns:
    - ModuleSetDeleteResponse: 모듈 세트 삭제 결과
        - resultCode (str): 처리 결과 코드
        - message (str): 처리 결과 메시지

    Raises:
    - 401 UNAUTHORIZED: 인증 실패
    - 404 NOT_FOUND: 존재하지 않는 모듈 세트 ID
    """
    return ModuleSetService.delete_module_set(session, module_set_id, token_data.user_pk)


