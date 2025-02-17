from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.core.database import get_session
from app.api.schemas import auth_schema
from app.services.auth_service import AuthService
from app.core.jwt import JWTPayload, jwt_handler

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post(
    "/register",
    response_model=auth_schema.RegisterResponse,
    summary="회원가입 API",
    description="새로운 사용자를 등록하는 API입니다. 중복된 ID 또는 이메일은 허용되지 않습니다.",
    responses={
        200: {
            "description": "회원가입 성공",
            "content": {
                "application/json": {
                    "example": {
                      "resultCode": "SUCCESS",
                      "message": "User registered successfully"
                    }
                }
            }
        },
        400: {
            "description": "잘못된 요청",
            "content": {
                "application/json": {
                    "examples": {
                        "Duplicate User ID": {
                            "summary": "중복된 사용자 ID 존재",
                            "value": {
                                "resultCode": "FAILURE",
                                "message": "User ID already exists",
                                "error_code": "BAD_REQUEST"
                            }
                        },
                        "Duplicate Email": {
                            "summary": "중복된 이메일 존재",
                            "value": {
                                "resultCode": "FAILURE",
                                "message": "Email is already exists",
                                "error_code": "BAD_REQUEST"
                            }
                        },
                    }
                }
            }
        },
        422: {
            "description": "필수 필드 누락",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "FAILURE",
                        "message": "Validation error",
                        "error_code": "VALIDATION_ERROR", 
                        "detail": {
                            "errors": [
                                {
                                    "loc": [
                                        "body",
                                        "email"
                                    ],
                                    "msg": "value is not a valid email address",
                                    "type": "value_error.email"
                                }
                            ]
                        },
                    }
                }
            },
        },
        500: {
            "description": "서버 오류",
            "content": {
                "application/json": {
                    "examples": {
                        "Database Error": {
                            "summary": "데이터베이스 트랜잭션 오류",
                            "value": {
                                "resultCode": "FAILURE", 
                                "message": "Database error occurred",
                                "error_code": "DATABASE_ERROR"
                            }
                        },
                        "Internal Server Error": {
                            "summary": "예기치 못한 서버 오류 발생",
                            "value": {
                                "resultCode": "FAILURE",
                                "message": "Internal server error",
                                "error_code": "INTERNAL_SERVER_ERROR"
                            }
                        }
                    }
                }
            }
        }
    },
)
async def register(request: auth_schema.RegisterRequest, session: Session = Depends(get_session)):
    return AuthService.register(session, request)


@router.post(
    "/login",
    response_model=auth_schema.LoginResponse,
    summary="로그인 API",
    description="사용자 로그인을 위한 API입니다. 사용자 ID 또는 이메일로 로그인할 수 있습니다.",
    responses={
        200: {
            "description": "로그인 성공",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "User logged in successfully",
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
                    }
                }
            }
        },
        401: {
            "description": "인증 실패",
            "content": {
                "application/json": {
                    "examples": {
                        "Unauthorized": {
                            "summary": "잘못된 자격 증명",
                            "value": {
                                "resultCode": "FAILURE",
                                "message": "Invalid credentials",
                                "error_code": "UNAUTHORIZED",
                                "detail": {
                                    "error": "Invalid user ID or password"
                                }
                            }
                        }
                    }
                }
            }
        },
        500: {
            "description": "서버 오류",
            "content": {
                "application/json": {
                    "examples": {
                        "DatabaseError": {
                            "summary": "데이터베이스 오류",
                            "value": {
                                "resultCode": "FAILURE",
                                "message": "User primary key is missing",
                                "error_code": "DATABASE_ERROR",
                                "detail": {
                                    "user_id": "user_id",
                                    "role_id": "role_id"
                                }
                            }
                        },
                        "JWTError": {
                            "summary": "JWT 오류",
                            "value": {
                                "resultCode": "FAILURE",
                                "message": "Failed to encrypt role",
                                "error_code": "JWT_ERROR",
                                "detail": {
                                    "error": "error message"
                                }
                            }
                        },
                        "RedisError": {
                            "summary": "Redis 오류",
                            "value": {
                                "resultCode": "FAILURE",
                                "message": "Redis store failed",
                                "error_code": "REDIS_ERROR",
                                "detail": {
                                    "error": "error message"
                                }
                            }
                        }
                    }
                }
            }
        }
    }
)
async def login(request: auth_schema.LoginRequest, session: Session = Depends(get_session)):
    return AuthService.login(session, request)

@router.post(
    "/refresh-token",
    response_model=auth_schema.TokenRefreshResponse,
    summary="토큰 갱신 API",
    description="리프레시 토큰을 사용하여 새로운 액세스 토큰과 리프레시 토큰을 발급받는 API입니다.",
    responses={
        200: {
            "description": "토큰 갱신 성공",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "Token refreshed successfully",
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
                    }
                }
            }
        },
        401: {
            "description": "인증 실패",
            "content": {
                "application/json": {
                    "examples": {
                        "Unauthorized": {
                            "summary": "잘못된 자격 증명",
                            "value": {
                                "resultCode": "FAILURE",
                                "message": "Invalid credentials",
                                "error_code": "UNAUTHORIZED",
                                "detail": {
                                    "error": "Invalid refresh token"
                                }
                            }
                        },
                        "ExpiredToken": {
                            "summary": "토큰 만료",
                            "value": {
                                "resultCode": "FAILURE",
                                "message": "Refresh token has expired",
                                "error_code": "UNAUTHORIZED",
                                "detail": {
                                    "error": "Token has expired"
                                }
                            }
                        }
                    }
                }
            }
        },
        422: {
            "resultCode": "FAILURE",
            "message": "Validation error",
            "error_code": "VALIDATION_ERROR",
            "detail": {
                "errors": [
                    {
                        "loc": [
                            "body",
                            "refresh_token"
                        ],
                        "msg": "field required",
                       "type": "value_error.missing"
                    }
                ]
            }
        },
        500: {
            "description": "서버 오류",
            "content": {
                "application/json": {
                    "examples": {
                        "JWTError": {
                            "summary": "JWT 오류",
                            "value": {
                                "resultCode": "FAILURE",
                                "message": "Failed to create refresh token",
                                "error_code": "JWT_ERROR",
                                "detail": {
                                    "error": "error message"
                                }
                            }
                        },
                        "RedisError": {
                            "summary": "Redis 오류",
                            "value": {
                                "resultCode": "FAILURE",
                                "message": "Redis store failed",
                                "error_code": "REDIS_ERROR",
                                "detail": {
                                    "error": "error message"
                                }
                            }
                        }
                    }
                }
            }
        }
    }
)
async def refresh_token(request: auth_schema.TokenRefreshRequest):
    return AuthService.refresh_access_token(request)

@router.post(
    "/logout",
    response_model=auth_schema.LogoutResponse,
    summary="로그아웃 API",
    description="사용자 로그아웃을 위한 API입니다.",
    responses={
        200: {
            "description": "로그아웃 성공",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "Logout successful"
                    }
                }
            }
        },
        401: {
            "description": "인증 실패",
            "content": {
                "application/json": {
                    "examples": {
                        "Unauthorized": {
                            "summary": "잘못된 자격 증명",
                            "value": {
                                "resultCode": "FAILURE",
                                "message": "Invalid token",
                                "error_code": "UNAUTHORIZED",
                                "detail": {
                                    "error": "Invalid token"
                                }
                            }
                        }
                    }
                }
            }
        },
        500: {
            "description": "서버 오류",
            "content": {
                "application/json": {
                    "examples": {
                        "JWTError": {
                            "summary": "JWT 오류",
                            "value": {
                                "resultCode": "FAILURE",
                                "message": "Failed to decode JWT token",
                                "error_code": "JWT_ERROR",
                                "detail": {
                                    "error": "error message"
                                }
                            }
                        },
                        "RedisError": {
                            "summary": "Redis 오류",
                            "value": {
                                "resultCode": "FAILURE",
                                "message": "Redis store failed",
                                "error_code": "REDIS_ERROR",
                                "detail": {
                                    "error": "error message"
                                }
                            }
                        }
                    }
                }
            }
        }
    }
)
async def logout(
    token_data: JWTPayload = Depends(jwt_handler.jwt_auth_dependency())
):
    return AuthService.logout(token_data)

@router.post(
    "/admin/login",
    response_model=auth_schema.LoginResponse,
    summary="어드민 로그인 API",
    description="어드민 로그인을 위한 API입니다. 관리자 권한이 있는 사용자만 로그인할 수 있습니다.",
    responses={
        200: {
            "description": "로그인 성공",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "SUCCESS",
                        "message": "Admin logged in successfully",
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
                    }
                }
            }
        },
        403: {
            "description": "권한 거부",
            "content": {
                "application/json": {
                    "example": {
                        "resultCode": "FAILURE",
                        "message": "Permission denied",
                        "error_code": "FORBIDDEN",
                        "detail": {
                            "error": "User does not have required role",
                            "allowed_roles": ["master", "semi"]
                        }
                    }
                }
            }
        }
    }
)
async def admin_login(request: auth_schema.LoginRequest, session: Session = Depends(get_session)):
    response = AuthService.login(session, request, allowed_roles=["master", "semi"])
    return response