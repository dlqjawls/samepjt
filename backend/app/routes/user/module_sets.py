from fastapi import APIRouter, Query
from typing import Optional
from app.services.user.module_sets import ModuleSetService
from app.schemas.user.module_sets import ModuleSetsResponse


router = APIRouter()


@router.get(
    "/module-sets",
    summary="모듈 세트 목록 조회",
    description="사용자가 선택 가능한 모듈 세트 목록을 조회합니다. 페이지네이션을 지원합니다.",
    response_model=ModuleSetsResponse,
    responses={
        200: {
            "description": "모듈 세트 목록 조회 성공",
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
        }
    }
)
async def get_module_sets(
    page: int = Query(1, description="페이지 번호 (최소 1)", gt=0), 
    page_size: int = Query(10, description="페이지 크기 (기본값: 10, 최소 1)", gt=0) 
):
    return ModuleSetService.get_module_sets(page, page_size)
