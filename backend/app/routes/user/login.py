from fastapi import APIRouter
from app.schemas.user.login import UserLoginRequest, UserLoginResponse
from app.services.user.login import UserLoginService

router = APIRouter()

@router.post(
    "/login",
    response_model=UserLoginResponse,
    summary="로그인",
    description="사용자 로그인 후 JWT 토큰을 반환합니다.",
    responses={
        200: {
            "description": "로그인 성공",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "Login successful",
                        "token": "eyJhbGciOi..."
                    }
                }
            }
        },
        401: {
            "description": "로그인 실패 - 잘못된 ID 또는 비밀번호",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "FAILURE",
                        "message": "Login failed",
                        "errors": [
                            {"field": "userId", "message": "User ID does not exist"},
                            {"field": "userPassword", "message": "Incorrect password"}
                        ]
                    }
                }
            },
        },
        422: {
            "description": "유효성 검사 실패 - 요청 형식 오류",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "userId"],
                                "msg": "field required",
                                "type": "value_error.missing"
                            }
                        ]
                    }
                }
            },
        },
    },
)
def login_user(user: UserLoginRequest):
    return UserLoginService.login_user(user)
