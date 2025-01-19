from fastapi import APIRouter
from typing import List
from app.models.user import UserRegisterRequest, UserRegisterResponse, UserLoginRequest, UserLoginResponse, UserSchema
from app.services.user_service import UserService
from app.dummy_data import dummy_users  # 더미 데이터

router = APIRouter(prefix="/user", tags=["User"])

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
    return UserService.register_user(user)


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
    return UserService.login_user(user)