from fastapi import APIRouter
from app.schemas.admin.login import AdminLoginRequest, AdminLoginResponse
from app.services.admin.login import AdminLoginService

router = APIRouter()

@router.post(
    "/login",
    response_model=AdminLoginResponse,
    summary="관리자 로그인",
    description="관리자 로그인 후 **JWT Access Token** 및 **Refresh Token**을 반환합니다.",
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
            "description": "로그인 실패 - 잘못된 관리자 ID 또는 비밀번호",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "FAILURE",
                        "message": "Login failed",
                        "errors": [
                            {"field": "adminId", "message": "Admin ID does not exist"},
                            {"field": "adminPassword", "message": "Incorrect password"}
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
                                "loc": ["body", "adminId"],
                                "msg": "field required",
                                "type": "value_error.missing"
                            },
                            {
                                "loc": ["body", "adminPassword"],
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
def login_admin(admin: AdminLoginRequest):
    return AdminLoginService.login_admin(admin)
