from fastapi import APIRouter, Depends, Path, Query
from sqlmodel import Session
from app.core.database import get_session
from app.core.jwt import JWTPayload, jwt_handler
from app.services.admin.module_service import ModuleService
from app.api.schemas.admin.module_schema import ModuleRegisterRequest, ModuleMessageResponse, ModuleGetResponse, ModuleUpdateRequest

router = APIRouter(
)

@router.get(
    "/modules",
    response_model=ModuleGetResponse,
    summary="🧳 모듈 목록 조회",
    description="관리자가 등록된 모듈 목록을 조회하는 API입니다. 모듈 타입 ID를 통한 페이지네이션을 지원합니다.",
    responses={
        200: {
            "description": "모듈 목록 조회 성공",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "모듈 목록 조회 성공",
                        "data": {
                            "modules": [
                                {
                                    "module_id": 1,
                                    "module_nfc_tag_id": "1A1FF1043E2BC6",
                                    "module_type_id": 2,
                                    "module_type_name": "medium",
                                    "last_maintenance_at": "2025-01-10T12:00:00",
                                    "next_maintenance_at": "2025-06-10T12:00:00",
                                    "item_status_id": 1,
                                    "item_status_name": "active",
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
        }
    }
)
def get_modules(
    page: int = Query(1, ge=1, description="결과 페이지 번호 (기본값: 1)"),
    pageSize: int = Query(10, ge=1, description="한 페이지당 반환할 모듈 개수 (기본값: 10)"),
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency(allowed_roles=["master", "semi"]))
):
    return ModuleService.get_module_list(session, page, pageSize)

@router.post(
    "/modules",
    response_model=ModuleMessageResponse,
    summary="🧳 모듈 등록",
    description="관리자가 새로운 모듈을 등록하는 API입니다.",
    status_code=201,
    responses={
        201: {
            "description": "모듈 등록 성공",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "Module registered successfully"
                    }
                }
            }
        }
    }
)
def register_module(
    module_data: ModuleRegisterRequest,
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency(allowed_roles=["master"]))
):
    return ModuleService.register_module(session, module_data, token_data.user_pk)
  
@router.patch(
    "/modules/{module_id}",
    response_model=ModuleMessageResponse,
    summary="🧳 모듈 수정",
    description="관리자가 등록된 모듈을 수정하는 API입니다.",
    responses={
        200: {
            "description": "모듈 수정 성공",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "Module updated successfully"
                    }
                }
            }
        }
    }
)
def update_module(
    module_data: ModuleUpdateRequest,
    module_id: int = Path(..., description="수정할 모듈의 ID", gt=0),
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency(allowed_roles=["master"]))
):
    return ModuleService.update_module(session, module_id, module_data, token_data.user_pk)

@router.delete(
    "/modules/{module_id}",
    response_model=ModuleMessageResponse,
    summary="🧳 모듈 삭제",
    description="관리자가 등록된 모듈을 삭제하는 API입니다.",
    responses={
        200: {
            "description": "모듈 삭제 성공",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "Module deleted successfully"
                    }
                }
            }
        }
    }
)
def delete_module(
    module_id: int = Path(..., description="삭제할 모듈의 ID", gt=0),
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency(allowed_roles=["master"]))
):
    return ModuleService.delete_module(session, module_id, token_data.user_pk)
