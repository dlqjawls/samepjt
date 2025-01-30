from fastapi import APIRouter, Path, Query, Depends
from sqlmodel import Session
from app.services.user.option_type_service import OptionTypeService
from app.api.schemas.user import option_type_schema
from app.core.database import get_session

router = APIRouter()

@router.get(
    "/option-types",
    summary="🔧 옵션 타입 목록 조회",
    description="사용자가 선택할 수 있는 **옵션 타입 목록**을 조회합니다. **페이지네이션을 지원합니다.**",
    response_model=option_type_schema.OptionTypesResponse,
    responses={
        200: {
            "description": "✅ 옵션 타입 목록 조회 성공",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "Option types retrieved successfully",
                        "data": {
                            "optionTypes": [
                                {
                                    "optionTypeId": 1,
                                    "optionTypeName": "배터리 팩",
                                    "optionTypeSize": "2x3x2",
                                    "description": "캠핑 모듈용 배터리 팩",
                                    "optionTypeCost": 100.0,
                                    "stockQuantity": 15,
                                    "imgUrls": ["https://example.com/option1.jpg"]
                                },
                                {
                                    "optionTypeId": 2,
                                    "optionTypeName": "냉장고",
                                    "optionTypeSize": "3x4x3",
                                    "description": "캠핑 모듈용 냉장고",
                                    "optionTypeCost": 200.0,
                                    "stockQuantity": 10,
                                    "imgUrls": ["https://example.com/option2.jpg"]
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
                    "example": {
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
)
async def get_option_types(
    page: int = Query(1,  description="📄 페이지 번호 (최소 1)",gt=0), 
    page_size: int = Query(10, description="📄 페이지 크기 (기본값: 10, 최소 1)", gt=0),
    session: Session = Depends(get_session)
):
    return OptionTypeService.get_all_option_types(session, page, page_size)


@router.get(
    "/option-types/{option_type_id}",
    summary="🔧 옵션 타입 상세 조회",
    description="특정 옵션 타입의 상세 정보를 조회합니다.",
    response_model=option_type_schema.OptionTypesResponse,
    responses={
        200: {
            "description": "✅ 옵션 타입 상세 조회 성공",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "Option type retrieved successfully",
                        "data": {
                            "optionTypeId": 1,
                            "optionTypeName": "배터리 팩",
                            "optionTypeSize": "2x3x2",
                            "description": "캠핑 모듈용 배터리 팩",
                            "optionTypeCost": 100.0,
                            "stockQuantity": 15,
                            "imgUrls": ["https://example.com/option1.jpg"]
                        }
                    }
                }
            }
        },
        404: {
            "description": "❌ 옵션 타입 없음",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "FAILURE",
                        "message": "Option type not found",
                        "error_code": "NOT_FOUND",
                        "detail": {
                            "option_type_id": 1
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
                                    "loc": ["path", "option_type_id"],
                                    "msg": "value is not a valid integer",
                                    "type": "type_error.integer"
                                }
                            ]
                        }
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
)
async def get_option_type_by_id(
  option_type_id: int = Path(..., description="🔍 옵션 타입 ID (최소 1)", gt=0),
  session: Session = Depends(get_session)
):
  return OptionTypeService.get_option_type_by_id(session, option_type_id)
