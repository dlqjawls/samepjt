from fastapi import APIRouter, Query, Depends
from sqlmodel import Session
from app.services.user.option_types import OptionTypeService
from app.api.schemas.user.option_types import OptionTypesResponse
from app.core.database import get_session

router = APIRouter()

@router.get(
    "/option-types",
    summary="🔧 옵션 타입 목록 조회",
    description="사용자가 선택할 수 있는 **옵션 타입 목록**을 조회합니다. **페이지네이션을 지원합니다.**",
    response_model=OptionTypesResponse,
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
            "description": "❌ 옵션 타입 없음",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "No option types found"
                    }
                }
            }
        }
    }
)
async def get_option_types(
    page: int = Query(1, description="📄 페이지 번호 (최소 1)", gt=0), 
    page_size: int = Query(10, description="📄 페이지 크기 (기본값: 10, 최소 1)", gt=0),
    session: Session = Depends(get_session)
):
    """
    🔍 **옵션 타입 목록 조회 API**
    - 사용자가 선택할 수 있는 **옵션 타입 목록**을 가져옵니다.
    - **페이지네이션 기능을 포함하여 조회 가능**
    - **존재하는 옵션 타입이 없을 경우 404 반환**
    """
    return OptionTypeService.get_all_option_types(session, page, page_size)


@router.get(
    "/option-types/{option_type_id}",
    summary="🔍 특정 옵션 타입 조회",
    description="**특정 옵션 타입의 상세 정보를 조회**합니다.",
    response_model=OptionTypesResponse,
    responses={
        200: {
            "description": "✅ 옵션 타입 조회 성공",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "Option type retrieved successfully",
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
                                }
                            ]
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
                        "detail": "Option type not found"
                    }
                }
            }
        }
    }
)
async def get_option_type_by_id(
    option_type_id: int,
    session: Session = Depends(get_session)
):
    """
    🔍 **특정 옵션 타입 조회 API**
    - 특정 옵션 타입의 **세부 정보**를 가져옵니다.
    - **존재하지 않는 옵션 타입 요청 시 404 반환**
    """
    return OptionTypeService.get_option_type_by_id(session, option_type_id)
