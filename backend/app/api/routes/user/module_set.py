from fastapi import APIRouter, Query, Depends
from typing import Optional
from app.services.user.module_set_service import ModuleSetService
from app.api.schemas.user.module_set_schema import ModuleSetsResponse
from app.core.database import Session, get_session

router = APIRouter()

@router.get(
    "/module-sets",
    summary="📦 모듈 세트 목록 조회",
    description="사용자가 선택 가능한 모듈 세트 목록을 조회합니다. **페이지네이션을 지원합니다.**",
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
                                    "imgUrls": ["https://example.com/module1.jpg"],
                                    "moduleTypeId":3,
                                    "moduleTypeName":"large",
                                    "moduleTypeSize":"3x3",
                                    "moduleTypeCost":5000,
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
        422: {
            "description": "유효성 검사 오류",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "FAILURE",
                        "message": "Validation error",
                        "error_code": "VALIDATION_ERROR",
                        "detail": {
                            "errors": [
                                {
                                    "loc": ["query", "page"],
                                    "msg": "ensure this value is greater than 0",
                                    "type": "value_error.number.not_gt",
                                    "ctx": {"limit_value": 0}
                                }
                            ]
                        },
                        "data": None
                    }
                }
            }
        },
        500: {
            "description": "서버 오류",
            "content": {
                "application/json": {
                    "examples": {
                        "DatabaseError": {
                            "summary": "데이터베이스 오류",
                            "value": {
                                "resultCode": "FAILURE",
                                "message": "Database error occurred",
                                "error_code": "DATABASE_ERROR",
                                "detail": {
                                    "error": "error message"
                                }
                            }
                        },
                        "InternalServerError": {
                            "summary": "예기치 못한 서버 오류 발생",
                            "value": {
                                "resultCode": "FAILURE",
                                "message": "Internal server error",
                                "error_code": "INTERNAL_SERVER_ERROR",
                                "detail": {
                                    "error": "error message"
                                }
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
    page_size: int = Query(10, description="페이지 크기 (기본값: 10, 최소 1)", gt=0),
    session: Session = Depends(get_session)
):
    return ModuleSetService.get_all_module_sets(session, page, page_size)
