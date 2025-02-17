from fastapi import APIRouter, Depends, Path, Query
from sqlmodel import Session
from app.core.database import get_session
from app.core.jwt import JWTPayload, jwt_handler
from app.services.admin.option_service import OptionService
from app.api.schemas.admin.option_schema import OptionGetResponse, OptionRegisterRequest, OptionUpdateRequest, OptionMessageResponse

router = APIRouter()

@router.get(
    "/options",
    response_model=OptionGetResponse,
    summary="🔧 옵션 목록 조회",
    description="관리자가 등록된 옵션 목록을 조회하는 API입니다. 옵션 타입 ID를 통한 페이지네이션을 지원합니다.",
    responses={
        200: {
            "description": "옵션 목록 조회 성공",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "옵션 목록 조회 성공",
                        "data": {
                            "options": [
                                {   
                                    "option_id": 101,
                                    "option_type_id": 1,
                                    "item_status_name": "active",
                                    "last_maintenance_at": "2025-01-10T12:00:00",
                                    "next_maintenance_at": "2025-06-10T12:00:00",
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
def get_options(
    page: int = Query(1, ge=1, description="결과 페이지 번호 (기본값: 1)"),
    pageSize: int = Query(10, ge=1, description="한 페이지당 반환할 옵션 개수 (기본값: 10)"),
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency(allowed_roles=["master", "semi"]))
):
    return OptionService.get_option_list(session, page, pageSize)

@router.post(
    "/options",
    response_model=OptionMessageResponse,
    summary="🔧 옵션 등록",
    description="관리자가 새로운 옵션을 등록하는 API입니다.",
    responses={
        200: {
            "description": "옵션 등록 성공",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "Option registered successfully"
                    }
                }
            }
        }
    }
)
def register_option(
    option_data: OptionRegisterRequest,
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency(allowed_roles=["master"]))
):
    return OptionService.register_option(session, option_data, token_data.user_pk)
  
# NOTE: 미사용 (변경할 항목이 없음)
# @router.patch(
#     "/options/{option_id}",
#     response_model=OptionMessageResponse,
#     summary="🔧 옵션 수정",
#     description="관리자가 등록된 옵션을 수정하는 API입니다.",
#     responses={
#         200: {
#             "description": "옵션 수정 성공",
#             "content": {
#                 "application/json": {
#                     "example": {
#                         "resultCode": "SUCCESS",
#                         "message": "Option updated successfully"
#                     }
#                 }
#             }
#         }
#     }
# )
# def update_option(
#     option_data: OptionUpdateRequest,
#     option_id: int = Path(..., description="수정할 옵션의 ID", gt=0),
#     session: Session = Depends(get_session),
#     token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency(allowed_roles=["master"]))
# ):
#     return OptionService.update_option(session, option_id, option_data, token_data.user_pk)

@router.delete(
    "/options/{option_id}",
    response_model=OptionMessageResponse,
    summary="🔧 옵션 삭제",
    description="관리자가 등록된 옵션을 삭제하는 API입니다.",
    responses={
        200: {
            "description": "옵션 삭제 성공",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "Option deleted successfully"
                    }
                }
            }
        }
    }
)
def delete_option(
    option_id: int = Path(..., description="삭제할 옵션의 ID", gt=0),
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency(allowed_roles=["master"]))
):
    return OptionService.delete_option(session, option_id, token_data.user_pk)
