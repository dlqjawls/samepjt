from fastapi import APIRouter, Query, Depends
from typing import Optional
from app.services.user.option_types import OptionTypeService
from app.api.schemas.user.option_types import OptionTypesResponse
from app.core.database import Session, get_session

router = APIRouter()

@router.get(
    "/option-types",
    summary="옵션 타입 목록 조회",
    description="사용자가 선택 가능한 개별 옵션 타입 목록을 조회합니다. 옵션별 수량 정보를 포함합니다.",
    response_model=OptionTypesResponse,
    responses={
        200: {
            "description": "옵션 타입 목록 조회 성공",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "Option types retrieved successfully",
                        "data": {
                            "optionTypes": [
                                {
                                    "optionTypeId": 3,
                                    "optionTypeName": "배터리 팩",
                                    "optionTypeSize": "2x3x2",
                                    "optionTypeCost": 500.0,
                                    "stockQuantity": 15,
                                    "imgUrls": ["https://example.com/option1.jpg"],
                                    "description": "캠핑 모듈용 배터리 팩"
                                }
                            ],
                            "pagination": {
                                "currentPage": 1,
                                "totalPages": 3,
                                "totalItems": 10,
                                "pageSize": 5
                            }
                        }
                    }
                }
            }
        }
    }
)
async def option_types(
  page: int = Query(1, description="페이지 번호 (최소 1)", gt=0),
  page_size: int = Query(10, description="페이지 크기 (기본값: 10, 최소 1)", gt=0),
  option_type_id: Optional[int] = Query(None, description="옵션 타입 ID로 검색 (선택)"),
  session: Session = Depends(get_session)
):
  return OptionTypeService.get_option_types(session, page, page_size, option_type_id)
