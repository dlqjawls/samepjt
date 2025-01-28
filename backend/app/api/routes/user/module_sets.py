from fastapi import APIRouter, Query, Depends
from typing import Optional
from app.services.user.module_sets import ModuleSetService
from app.api.schemas.user.module_sets import ModuleSetsResponse
from app.core.database import Session, get_session

router = APIRouter()

@router.get(
    "/module-sets",
    summary="🛠️ 모듈 세트 목록 조회",
    description="사용자가 선택 가능한 모듈 세트 목록을 조회합니다. **페이지네이션을 지원합니다.**",
    response_model=ModuleSetsResponse,
    responses={
        200: {
            "description": "✅ 모듈 세트 목록 조회 성공",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "Module sets retrieved successfully",
                        "data": {
                            "moduleSets": [
                                {
                                    "moduleSetId": 1,
                                    "moduleSetName": "캠핑카 모듈 세트",
                                    "description": "캠핑에 최적화된 모듈 세트입니다.",
                                    "basePrice": 2500.0,
                                    "imgsUrls": ["https://example.com/module1.jpg"],
                                    "moduleSetOptionTypes": [
                                        {
                                            "optionTypeId": 101,
                                            "optionTypeName": "배터리 팩",
                                            "quantity": 2
                                        },
                                        {
                                            "optionTypeId": 102,
                                            "optionTypeName": "냉장고",
                                            "quantity": 1
                                        }
                                    ]
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
        404: {
            "description": "❌ 모듈 세트 없음",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "No module sets found"
                    }
                }
            }
        }
    }
)
async def get_module_sets(
    page: int = Query(1, description="📄 페이지 번호 (최소 1)", gt=0), 
    page_size: int = Query(10, description="📄 페이지 크기 (기본값: 10, 최소 1)", gt=0),
    session: Session = Depends(get_session)
):
    """
    🔍 **모듈 세트 목록 조회 API**
    - 사용자가 선택할 수 있는 모듈 세트 목록을 가져옵니다.
    - **페이지네이션 기능을 포함하여 조회 가능**
    - **존재하는 모듈 세트가 없을 경우 404 반환**
    """
    return ModuleSetService.get_all_module_sets(session, page, page_size)
