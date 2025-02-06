from pydantic import BaseModel, Field
from app.api.schemas.common import ResponseBase

class MeRentInfo(BaseModel):
    """현재 로그인한 사용자의 진행중인 렌트 정보 모델"""
    rent_id: int = Field(..., example=1)

class MeRentInfoResponse(ResponseBase[MeRentInfo]):
    """현재 사용자 렌트 정보 조회 응답 모델"""
    class Config:
        schema_extra = {
            "example": {
                "resultCode": "SUCCESS",
                "message": "Current rent info retrieved successfully",
                "data": {
                    "rent_id": 1
                }
            }
        } 