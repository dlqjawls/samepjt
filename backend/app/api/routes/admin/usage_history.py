from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from app.api.schemas.admin.usage_history_schema import UsageHistoryGetResponse
from app.core.database import get_session
from app.core.jwt import JWTPayload, jwt_handler
from app.services.admin.usage_history_service import UsageHistoryService

router = APIRouter()

@router.get(
    "/usage-history",
    response_model=UsageHistoryGetResponse,
    summary="🔍 사용 이력 조회",
    description="특정 페이지의 사용 이력을 조회합니다. 삭제된 항목 포함 여부를 선택할 수 있습니다.",
    responses={
        200: {
            "description": "사용 이력 조회 성공",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "사용 이력 조회 성공",
                        "data": {
                            "usage_history": [
                                {
                                    "usage_id": 1,
                                    "rent_id": 1,
                                    "item_id": 1,
                                    "item_type_name": "vehicle",
                                    "usage_status_name": "in_use",
                                    "created_at": "2025-01-01 12:00:00",
                                    "updated_at": "2025-01-01 12:00:00"
                                },
                                {
                                    "usage_id": 2,
                                    "rent_id": 1,
                                    "item_id": 3,
                                    "item_type_name": "module",
                                    "usage_status_name": "in_use",
                                    "created_at": "2025-01-01 12:00:00",
                                    "updated_at": "2025-01-01 12:00:00"
                                } 
                            ],
                            "pagination": {
                                "currentPage": 1,
                                "totalPages": 1,
                                "totalItems": 1,
                                "pageSize": 10
                            }
                        }
                    }
                }
            }
        }
    }
)
def get_usage_history(
    page: int = Query(1, gt=0, description="현재 페이지 번호"),
    page_size: int = Query(10, gt=0, description="한 페이지 당 사용 이력 수"),
    include_deleted: bool = Query(False, description="삭제된 항목 포함 여부"),
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency(allowed_roles=["master", "semi"]))
):
    return UsageHistoryService.get_usage_history(session, page, page_size, include_deleted = True)