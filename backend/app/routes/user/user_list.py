from fastapi import APIRouter
from typing import List
from app.schemas.user.user_list import UserSchema
from app.dummy_data import dummy_users  # 더미 데이터

router = APIRouter()

@router.get(
    "/list",
    summary="사용자 목록 조회",
    description="더미 사용자 데이터를 반환합니다. (개발용)",
    response_model=List[UserSchema],
    responses={
        200: {
            "description": "사용자 목록 조회 성공",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "userId": "john_doe",
                            "userPassword": "securepassword",
                            "userEmail": "john@example.com",
                            "userName": "John Doe",
                            "userPhoneNum": "010-1234-5678",
                            "userAddress": "123 Main St, City, Country"
                        }
                    ]
                }
            }
        }
    },
)
def get_user_list():
    return dummy_users
