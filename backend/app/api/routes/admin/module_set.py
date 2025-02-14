from fastapi import APIRouter, Depends, File, Query, Path, UploadFile
from sqlmodel import Session
from app.core.database import get_session
from app.core.jwt import JWTPayload, jwt_handler
from app.services.admin.module_set_service import ModuleSetService
from app.api.schemas.admin.module_set_schema import ModuleSetGetResponse, ModuleSetRegisterRequest, ModuleSetMessageResponse, ModuleSetUpdateRequest, ModuleSetRemoveImageRequest, ModuleSetAddOptionRequest


router = APIRouter()

@router.get(
    "/module-sets",
    response_model=ModuleSetGetResponse,
    summary="📦 모듈 세트 목록 조회",
    description="등록된 모듈 세트 목록을 페이지네이션 방식으로 조회합니다.",
    responses={
        200: {
            "description": "모듈 세트 목록 조회 성공",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "Module set data retrieved successfully",
                        "data": {
                                    "module_sets": [
                                        {
                                    "module_set_id": 1,
                                    "module_set_name": "캠핑카 모듈 세트",
                                    "description": "캠핑을 위한 완벽한 모듈 세트",
                                    "module_set_images": [  
                                      "https://example.com/images/module-set-101.jpg", 
                                      "https://example.com/images/module-set-102.jpg"
                                    ],
                                    "module_set_features": "배터리 팩, 태양광 패널 포함",
                                    "module_type_id": 1,
                                    "cost": 1400,
                                    "module_set_option_types": [
                                        {
                                            "optionTypeId": 201,
                                            "optionTypeName": "배터리 팩",
                                            "quantity": 1
                                        },
                                        {
                                            "optionTypeId": 202,
                                            "optionTypeName": "냉장고",
                                            "quantity": 2
                                        }
                                    ],
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
async def get_module_set_list(
    page: int = Query(1, gt=0, description="현재 페이지 (최소 1)"),
    pageSize: int = Query(10, gt=0, description="페이지 당 모듈 세트 개수 (최소 1)"),
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency(allowed_roles=["semi", "master"]))
):
    return ModuleSetService.get_module_set_list(session, page, pageSize)

@router.post(
    "/module-sets",
    response_model=ModuleSetMessageResponse,
    summary="📦 모듈 세트 등록",
    description=(
        "새로운 모듈 세트를 등록하는 API입니다. 여러 이미지를 업로드할 수 있습니다."
    ),
    responses={
        200: {
            "description": "모듈 세트 등록 성공",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "Module set created successfully"
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
        403: {
            "description": "권한 없음",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "FAILURE",
                        "message": "Permission denied",
                        "error_code": "FORBIDDEN"
                    } 
                }
            }
        },
        422: {
            "description": "유효하지 않은 입력",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "FAILURE",
                        "message": "Validation error",
                        "error_code": "VALIDATION_ERROR",
                        "detail": {"errors": [{"field": "module_type_id", "message": "Invalid module type id"}]}  
                    }
                }
            }
        }
    }
)
async def create_module_set(
    register_request: ModuleSetRegisterRequest,
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency(allowed_roles=["master"]))
) -> ModuleSetMessageResponse:
    return ModuleSetService.register_module_set(session, register_request, token_data.user_pk)

@router.patch(
    "/module-sets/{module_set_id}",
    response_model=ModuleSetMessageResponse,
    summary="📦 모듈 세트 수정",
    description="기존 모듈 세트를 수정하는 API입니다.",
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
    request: ModuleSetUpdateRequest,
    module_set_id: int = Path(..., description="모듈 세트 ID (최소 1)", gt=0),
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency(allowed_roles=["master"]))
) -> ModuleSetMessageResponse:
    return ModuleSetService.update_module_set(
        session,
        module_set_id,
        request,
        token_data.user_pk
    )     

@router.delete(
    "/module-sets/{module_set_id}",
    response_model=ModuleSetMessageResponse,
    summary="📦 모듈 세트 삭제",
    description="기존 모듈 세트를 삭제하는 API입니다.",
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
    module_set_id: int = Path(..., description="모듈 세트 ID (최소 1)", gt=0),
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency(allowed_roles=["master"]))
) -> ModuleSetMessageResponse:
    return ModuleSetService.delete_module_set(session, module_set_id, token_data.user_pk)

@router.post(
    "/module-sets/{module_set_id}/images",
    response_model=ModuleSetMessageResponse,
    summary="📦 모듈 세트 이미지 추가",
    description="모듈 세트에 이미지를 추가하는 API입니다.",
    responses={
        200: {
            "description": "모듈 세트 이미지 추가 성공",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "Module set image added successfully"
                    }
                }
            }
        }
    }
)
async def add_module_set_image(
    module_set_id: int = Path(..., description="모듈 세트 ID (최소 1)", gt=0),
    images: UploadFile = File(...),
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency(allowed_roles=["master"]))
) -> ModuleSetMessageResponse:
    return ModuleSetService.add_module_set_image(session, module_set_id, images)    

@router.delete(
    "/module-sets/{module_set_id}/images",
    response_model=ModuleSetMessageResponse,  
    summary="📦 모듈 세트 이미지 삭제",
    description="모듈 세트에 이미지를 삭제하는 API입니다.",
    responses={
        200: {
            "description": "모듈 세트 이미지 삭제 성공",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "Module set image removed successfully"  
                    }
                }
            }
        }
    }
)
async def remove_module_set_image(  
    request: ModuleSetRemoveImageRequest,
    module_set_id: int = Path(..., description="모듈 세트 ID (최소 1)", gt=0),
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency(allowed_roles=["master"]))
) -> ModuleSetMessageResponse:
    return ModuleSetService.remove_module_set_image(session, module_set_id, request)      
  

@router.post(
    "/module-sets/{module_set_id}/options",
    response_model=ModuleSetMessageResponse,
    summary="📦 모듈 세트 옵션 추가",
    description="모듈 세트에 옵션을 추가하는 API입니다.",
    responses={
        200: {
            "description": "모듈 세트 옵션 추가 성공",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "Module set option added successfully"
                    }
                } 
            }
        }
    }
)
async def add_module_set_option(
    request: ModuleSetAddOptionRequest,
    module_set_id: int = Path(..., description="모듈 세트 ID (최소 1)", gt=0),  
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency(allowed_roles=["master"]))
) -> ModuleSetMessageResponse:
    return ModuleSetService.add_module_set_option(session, module_set_id, request)   


@router.delete(
    "/module-sets/{module_set_id}/options/{option_type_id}",
    response_model=ModuleSetMessageResponse,
    summary="📦 모듈 세트 옵션 삭제",
    description="모듈 세트에 옵션을 삭제하는 API입니다.",
    responses={
        200: {
            "description": "모듈 세트 옵션 삭제 성공",
            "content": {
                "application/json": { 
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "Module set option removed successfully"
                    }
                }
            }
        }
    }
)
async def remove_module_set_option(
    module_set_id: int = Path(..., description="모듈 세트 ID (최소 1)", gt=0),
    option_type_id: int = Path(..., description="옵션 타입 ID (최소 1)", gt=0),  
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency(allowed_roles=["master"]))
) -> ModuleSetMessageResponse:
    return ModuleSetService.remove_module_set_option(session, module_set_id, option_type_id)


              


