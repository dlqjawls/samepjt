from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.core.database import get_session
from app.services.user.rent_service import RentService
from app.api.schemas.user.rent import CancelRentRequest, RentRequest, RentResponse
from app.core.jwt import JWTPayload, jwt_handler

router = APIRouter()

@router.post(
    "/rent",
    response_model=RentResponse,
    summary="🚗 렌트 요청",
    description="사용자가 차량, 모듈, 옵션을 선택하여 **렌트 요청**을 생성합니다.",
    responses={
        200: {
            "description": "✅ 렌트 성공",
            "content": {
                "application/json": {
                    "example": {
                        "rent_id": 123,
                        "vehicle_number": 45
                    }
                }
            }
        },
        404: {
            "description": "❌ 렌트 실패 - 사용 가능한 차량, 모듈, 옵션 부족",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "No available vehicle found"
                    }
                }
            }
        },
        422: {
            "description": "⚠️ 유효성 검사 실패 - 요청 형식 오류",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "rentStartDate"],
                                "msg": "invalid datetime format",
                                "type": "value_error.datetime"
                            },
                            {
                                "loc": ["body", "autonomousArrivalPoint", "x"],
                                "msg": "float required",
                                "type": "type_error.float"
                            }
                        ]
                    }
                }
            }
        },
    },
)
async def rent_vehicle(
    rent_request: RentRequest,
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency())
):
    """
    🚀 **렌트 요청 API**
    - 사용자는 차량, 모듈 및 옵션을 선택하여 렌트를 요청할 수 있습니다.
    - **사용 가능한 차량, 모듈이 없는 경우 404 에러 반환**
    - **렌트 생성 후 차량, 모듈, 옵션의 상태가 ACTIVE(사용 중)로 변경**
    """
    rent_result = RentService.create_rent(session, rent_request, token_data.user_pk)
    return rent_result


@router.delete(
    "/rent/{rent_id}",
    summary="🚗 렌트 취소 (소프트 딜리트)",
    description="렌트 요청을 **취소**합니다. (`status_id=4`로 변경)",
    responses={
        200: {"description": "✅ 렌트 취소 성공"},
        404: {"description": "❌ 렌트 기록 없음"},
        400: {"description": "⚠️ 이미 취소되었거나 완료된 렌트"}
    }
)
async def soft_delete_rent(
    cancel_rent_request: CancelRentRequest,
    session: Session = Depends(get_session),
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency())
):
    """
    🛑 **렌트 취소 API**
    - 사용자는 진행 중인 렌트를 취소할 수 있습니다.
    - **렌트가 이미 취소(CANCELED) 또는 완료(COMPLETED)된 경우 400 에러 반환**
    - **취소된 차량, 모듈 및 옵션은 다시 INACTIVE 상태로 변경됨**
    """
    rent_result = RentService.cancel_rent(session, cancel_rent_request, token_data.user_pk)
    return rent_result
