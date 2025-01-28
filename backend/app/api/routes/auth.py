from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.core.database import get_session
from app.api.schemas import auth_schema
from app.services.auth_service import AuthService
from app.core.jwt import JWTPayload, jwt_handler

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post(
    "/register",
    response_model=auth_schema.RegisterResponse,
    summary="📝 회원가입",
    description="새로운 사용자를 등록합니다.",
    responses={
        200: {
            "description": "✅ 회원가입 성공",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "User registered successfully",
                        "errors": []
                    }
                }
            }
        },
        400: {
            "description": "❌ 회원가입 실패 - 중복된 ID 또는 이메일",
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
        422: {
            "description": "❗ 유효성 검사 실패 - 요청 형식 오류",
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
async def register(request: auth_schema.RegisterRequest, session: Session = Depends(get_session)):
    return AuthService.register(session, request)

@router.post(
    "/login",
    response_model=auth_schema.LoginResponse,
    summary="🔑 사용자 로그인",
    description="사용자가 로그인하고 **JWT Access Token** 및 **Refresh Token**을 발급받습니다.",
    responses={
        200: {
            "description": "✅ 로그인 성공",
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
            "description": "❌ 로그인 실패 - 잘못된 사용자 ID 또는 비밀번호",
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
            "description": "❗ 유효성 검사 실패 - 요청 형식 오류",
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
async def login(request: auth_schema.LoginRequest, session: Session = Depends(get_session)):
    return AuthService.login(session, request)

@router.post(
    "/refresh-token",
    response_model=auth_schema.TokenRefreshResponse,
    summary="🔄 액세스 토큰 재발급",
    description="✅ `Refresh Token`을 이용해 새로운 `Access Token`을 발급받습니다. "
                "이전 리프레시 토큰을 폐기하고 새로운 리프레시 토큰을 발급합니다.",
    responses={
        200: {
            "description": "✅ 토큰 재발급 성공",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOi...",
                        "refresh_token": "eyJhbGciOi..."
                    }
                }
            }
        },
        401: {
            "description": "❌ 토큰 재발급 실패 - 유효하지 않은 리프레시 토큰",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid refresh token"
                    }
                }
            },
        },
    },
)
async def refresh_token(request: auth_schema.TokenRefreshRequest):
    return AuthService.refresh_access_token(request)

@router.post(
    "/logout",
    response_model=auth_schema.LogoutResponse,
    summary="🚪 로그아웃",
    description="사용자가 로그아웃하여 **Refresh Token**을 무효화합니다. "
                "이후 해당 리프레시 토큰으로 새로운 액세스 토큰을 발급할 수 없습니다.",
    responses={
        200: {
            "description": "✅ 로그아웃 성공",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Successfully logged out"
                    }
                }
            }
        },
        401: {
            "description": "❌ 로그아웃 실패 - 유효하지 않은 토큰",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid token data"
                    }
                }
            },
        },
    },
)
async def logout(
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency())
):
    return AuthService.logout(token_data)


@router.post(
    "/admin/login",
    response_model=auth_schema.LoginResponse,
    summary="🔑 관리자 로그인",
    description="관리자가 로그인하고 **JWT Access Token** 및 **Refresh Token**을 발급받습니다. **관리자(`master`, `semi`)만 허용됩니다.**",
    responses={
        200: {
            "description": "✅ 로그인 성공",
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
            "description": "❌ 로그인 실패 - 잘못된 사용자 ID 또는 비밀번호",
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
        403: {
            "description": "❌ 로그인 실패 - 권한 부족 (관리자만 허용)",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "FAILURE",
                        "message": "Access denied: Only admins can log in",
                        "errors": []
                    }
                }
            }
        }
    },
)
async def admin_login(request: auth_schema.LoginRequest, session: Session = Depends(get_session)):
    response = AuthService.login(session, request, allowed_roles=["master", "semi"])
    return response
