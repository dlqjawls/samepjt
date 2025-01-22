from fastapi import APIRouter
from app.schemas.user.login import UserLoginRequest, UserLoginResponse
from app.services.user.login import UserLoginService

router = APIRouter()

@router.post(
    "/login",
    response_model=UserLoginResponse,
    summary="사용자 로그인",
    description="사용자 로그인 후 **JWT Access Token** 및 **Refresh Token**을 반환합니다.",
    responses={
        200: {
            "description": "로그인 성공",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "Login successful",
                        "accessToken": "eyJhbGciOi...",
                        "refreshToken": "eyJhbGciOi...",
                        "errors": []
                    }
                }
            }
        },
        401: {
            "description": "로그인 실패 - 잘못된 사용자 ID 또는 비밀번호",
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
                            },
                            {
                                "loc": ["body", "userPassword"],
                                "msg": "ensure this value has at least 6 characters",
                                "type": "value_error.any_str.min_length",
                            }
                        ]
                    }
                }
            },
        },
    },
)
def login_user(user: UserLoginRequest):
    """사용자 로그인 요청을 처리하는 엔드포인트"""
    return UserLoginService.login_user(user)
