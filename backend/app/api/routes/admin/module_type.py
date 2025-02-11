from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.core.database import get_session
from app.services.admin.module_type_service import ModuleTypeService
from app.api.schemas.admin.module_type_schema import ModuleTypesResponse
from app.core.jwt import jwt_handler, JWTPayload

router = APIRouter(
)

@router.get(
    "/module-types",
    response_model=ModuleTypesResponse,
    summary="♟ 모듈 타입 목록 조회",
    description="관리자가 등록된 모듈 타입 목록을 조회합니다.",
    responses={
        200: {
            "description": "모듈 타입 목록 조회 성공",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "Module types retrieved successfully",
                        "data": {
                            "module_types": [
                                {
                                    "module_type_id": 1,
                                    "module_type_name": "small",
                                    "module_type_size": "1.2m x 2.5m",
                                    "module_type_cost": 500.00
                                },
                                {
                                    "module_type_id": 2,
                                    "module_type_name": "medium",
                                    "module_type_size": "2.0m x 3.5m",
                                    "module_type_cost": 800.00
                                }
                            ]
                        }
                    }
                }
            }
        },
        401: {"description": "인증 실패"},
        403: {"description": "권한 없음"},
        500: {"description": "서버 오류"}
    }
)
async def get_module_types(
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency(["semi", "master"]))
) -> ModuleTypesResponse:
    return ModuleTypeService.get_all_module_types(session)
