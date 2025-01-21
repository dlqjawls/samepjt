from fastapi import APIRouter
from app.schemas.user.register import UserRegisterRequest, UserRegisterResponse
from app.services.user.register import UserRegisterService

router = APIRouter()

@router.post(
    "/register",
    response_model=UserRegisterResponse,
    summary="회원가입",
    description="새로운 사용자를 등록합니다.",
    responses={
        200: {"description": "회원가입 성공"},
        400: {
            "description": "회원가입 실패 - 중복된 ID 또는 이메일",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "FAILURE",
                        "message": "User registration failed",
                        "errors": [
                            {"field": "userId", "message": "User ID already exists"},
                            {"field": "userEmail", "message": "Email is already registered"}
                        ]
                    }
                }
            },
        },
    },
)
def register_user(user: UserRegisterRequest):
    return UserRegisterService.register_user(user)
