from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.core.database import get_session
from app.services.user.rent_service import create_rent
from app.api.schemas.user.rent import RentRequest, RentResponse
from app.core.jwt import jwt_handler

router = APIRouter(prefix="/rent", tags=["Rent"])

@router.post(
    "/rent",
    response_model=RentResponse,
    summary="렌트 요청",
    description="사용자가 차량, 모듈, 옵션을 선택하여 **렌트 요청**을 생성합니다.",
    responses={
        200: {
            "description": "렌트 성공",
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
            "description": "렌트 실패 - 사용 가능한 차량, 모듈, 옵션 부족",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "No available vehicle found"
                    }
                }
            }
        },
        422: {
            "description": "유효성 검사 실패 - 요청 형식 오류",
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
    token_data: dict = Depends(jwt_handler.jwt_auth_dependency())
):
    """ 🚗 렌트 요청 API """
    rent_result = create_rent(session, rent_request, token_data["user_pk"])
    return rent_result
