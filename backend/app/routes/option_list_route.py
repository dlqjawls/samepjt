from fastapi import APIRouter, Query
from typing import Optional
from app.services.option_list_service import OptionService
from app.models.option_list import OptionListResponse

router = APIRouter(prefix="/user/option", tags=["Option"])

@router.get(
    "/list",
    summary="옵션 목록 조회",
    description="사용자가 선택 가능한 개별 옵션 목록을 조회합니다. 페이지네이션 및 검색을 지원합니다.",
    response_model=OptionListResponse,
    responses={
        200: {
            "description": "옵션 목록 조회 성공",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "Options retrieved successfully",
                        "data": {
                            "options": [
                                {
                                    "optionId": 201,
                                    "optionName": "배터리 팩",
                                    "optionSize": "2x3x2",
                                    "optionCost": 500,
                                    "optionType": "switch",
                                    "stockQuantity": 10,
                                    "imgUrls": ["https://example.com/option1.jpg"],
                                    "description": "캠핑 모듈용 배터리 팩"
                                }
                            ],
                            "pagination": {
                                "currentPage": 1,
                                "totalPages": 3,
                                "totalItems": 25,
                                "pageSize": 10
                            }
                        }
                    }
                }
            }
        },
        404: {
            "description": "검색 결과가 없거나 옵션 목록이 없음",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "FAILURE",
                        "message": "No matching options found",
                        "data": None
                    }
                }
            }
        }
    }
)
async def option_list(
    page: int = Query(1, description="페이지 번호 (최소 1)", gt=0),
    page_size: int = Query(10, description="페이지 크기 (기본값: 10, 최소 1)", gt=0),
    option_id: Optional[int] = Query(None, description="옵션 ID 검색 (선택)")
):
    """
    ✅ 옵션 목록 조회 API

    - 사용자가 선택 가능한 개별 옵션 목록을 조회합니다.
    - 페이지네이션 지원 (page, page_size).
    - `optionId`로 검색 가능.
    """
    return OptionService.get_options(page, page_size, option_id)
