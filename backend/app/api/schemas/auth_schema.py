from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

from app.api.schemas.common import ResponseBase

class RegisterRequest(BaseModel):
    """회원가입 요청 모델"""
    id: str = Field(..., min_length=3, example="newUser")
    password: str = Field(..., min_length=6, example="password123")
    email: EmailStr = Field(..., example="new@example.com")
    name: str = Field(..., example="newUser")
    phoneNum: str = Field(..., example="010-1234-5678")
    address: str = Field(..., example="Seoul, South Korea")

class RegisterResponse(ResponseBase[None]):
    """회원가입 응답 모델"""
    @classmethod
    def success(cls, message: str = "User registered successfully", data: Optional[None] = None) -> "RegisterResponse":
        """회원가입 성공 응답"""
        return super().success(message=message, data=data)
        
class LoginRequest(BaseModel):
    """로그인 요청 모델"""
    id: str = Field(..., min_length=3, example="user")
    password: str = Field(..., min_length=6, example="user123")

class LoginResponse(BaseModel):
    """로그인 응답 모델"""
    resultCode: str = Field(..., example="SUCCESS")
    message: str = Field(..., example="Login successful")
    accessToken: str = Field(..., example="eyJhbGciOiJ...")
    refreshToken: str = Field(..., example="eyJhbGciOiJ...")
    errors: Optional[List[str]] = Field(None, example=["Incorrect password"])

class TokenRefreshRequest(BaseModel):
    """액세스 토큰 재발급 요청 모델"""
    refresh_token: str = Field(..., example="eyJhbGciOiJIUzI1...")

class TokenRefreshResponse(BaseModel):
    """액세스 토큰 재발급 응답 모델"""
    access_token: str = Field(..., example="eyJhbGciOiJ...")
    refresh_token: str = Field(..., example="eyJhbGciOiJ...")

class LogoutResponse(BaseModel):
    """로그아웃 응답 모델"""
    message: str = Field(..., example="Successfully logged out")
