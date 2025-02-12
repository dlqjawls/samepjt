from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, Query, Path, UploadFile
from sqlmodel import Session
from app.core.database import get_session
from app.core.jwt import JWTPayload, jwt_handler
from app.services.admin.module_set_service import ModuleSetService
from app.api.schemas.admin.module_set_schema import ModuleSetGetResponse, ModuleSetRegisterRequest, ModuleSetRegisterResponse, ModuleSetUpdateRequest, ModuleSetUpdateResponse, ModuleSetDeleteResponse
import json

from app.utils.exceptions import BadRequestError, ValidationError

router = APIRouter()

@router.get(
    "/module-sets",
    response_model=ModuleSetGetResponse,
    summary="📦 관리자 모듈 세트 목록 조회",
    description="관리자가 등록된 모듈 세트 목록을 페이지네이션 방식으로 조회합니다.",
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
    response_model=ModuleSetRegisterResponse,
    summary="📦 모듈 세트 등록",
    description=(
        "관리자가 새로운 모듈 세트를 등록하는 API입니다. 여러 이미지를 업로드할 수 있습니다."
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
    module_set_name: str = Form(..., description="모듈 세트 이름"),
    description: str = Form(..., description="모듈 세트 설명"),
    module_type_id: int = Form(..., description="모듈 타입 ID", gt=0, le=3),
    module_set_features: Optional[str] = Form(None, description="모듈 세트 특징 (선택)"),
    module_set_images: Optional[List[UploadFile]] = File(
        None, 
        description="모듈 세트 이미지 파일 목록. 'Add string item' 버튼을 눌러 여러 파일을 첨부할 수 있습니다."
    ),
    options: Optional[str] = Form(
        None,
        description=(
            "모듈 세트 옵션 목록을 JSON 문자열로 전달합니다. 예: "
            "'[{\"option_type_id\": 201, \"quantity\": 1}, {\"option_type_id\": 202, \"quantity\": 2}]'"
        )
    ),
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency(allowed_roles=["master"]))
) -> ModuleSetRegisterResponse:
    # JSON 문자열로 넘어온 옵션 필드를 파싱합니다.
    try:
        options_list = json.loads(options) if options else []
    except Exception as e:
        raise BadRequestError(message="옵션 필드 파싱 실패 : " + str(e))

    # 요청 데이터를 딕셔너리 형태로 정리한 후 Pydantic 모델로 변환
    request_data = {
        "module_set_name": module_set_name,
        "description": description,
        "module_type_id": module_type_id,
        "module_set_features": module_set_features,
        "module_set_images": module_set_images,  # List[UploadFile] 그대로 전달 (서비스 레이어에서 image.file 사용)
        "options": options_list
    }
    try:
        register_request = ModuleSetRegisterRequest.parse_obj(request_data)
    except Exception as e:
        raise ValidationError(message="요청 데이터 검증 실패 : " + str(e))
    
    response = ModuleSetService.register_module_set(session, register_request, token_data.user_pk)
    return response

@router.patch(
    "/module-sets/{module_set_id}",
    response_model=ModuleSetUpdateResponse,
    summary="📦 모듈 세트 수정",
    description="관리자가 기존 모듈 세트를 수정하는 API입니다.",
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
    module_set_id: int = Path(..., description="모듈 세트 ID (최소 1)", gt=0),
    module_set_name: Optional[str] = Form(None, description="모듈 세트 이름"),
    description: Optional[str] = Form(None, description="모듈 세트 설명"),
    module_type_id: Optional[int] = Form(None, description="모듈 타입 ID", gt=0, le=3),
    module_set_features: Optional[str] = Form(None, description="모듈 세트 특징 (선택)"),
    module_set_images: Optional[List[UploadFile]] = File(
        None, 
        description="모듈 세트 이미지 파일 목록. 'Add string item' 버튼을 눌러 여러 파일을 첨부할 수 있습니다."
    ),  
    options: Optional[str] = Form(
        None,
        description=(
            "모듈 세트 옵션 목록을 JSON 문자열로 전달합니다. 예: "
            "'[{\"option_type_id\": 201, \"quantity\": 1}, {\"option_type_id\": 202, \"quantity\": 2}]'"
        ) 
    ),
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency(allowed_roles=["master"]))
  ) -> ModuleSetUpdateResponse:
    # JSON 문자열로 넘어온 옵션 필드를 파싱합니다.
    try:
        options_list = json.loads(options) if options else []
    except Exception as e:
        raise BadRequestError(message="옵션 필드 파싱 실패 : " + str(e))

    # 요청 데이터를 딕셔너리 형태로 정리한 후 Pydantic 모델로 변환
    request_data = {
        "module_set_name": module_set_name,
        "description": description,
        "module_type_id": module_type_id,
        "module_set_features": module_set_features,
        "module_set_images": module_set_images,
        "options": options_list
    }
    return ModuleSetService.update_module_set(
        session=session,
        module_set_id=module_set_id,
        update_data=ModuleSetUpdateRequest.parse_obj(request_data),
        user_pk=token_data.user_pk
    )     

@router.delete(
    "/module-sets/{module_set_id}",
    response_model=ModuleSetDeleteResponse,
    summary="📦 모듈 세트 삭제",
    description="관리자가 기존 모듈 세트를 삭제하는 API입니다.",
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
) -> ModuleSetDeleteResponse:
    return ModuleSetService.delete_module_set(session, module_set_id, token_data.user_pk)


