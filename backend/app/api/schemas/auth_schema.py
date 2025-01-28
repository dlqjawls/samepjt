from pydantic import BaseModel, EmailStr, Field
from app.api.schemas.common import ResponseBase

# Request Models
class RegisterRequest(BaseModel):
    id: str = Field(..., min_length=3, example="newUser")
    password: str = Field(..., min_length=6, example="password123")
    email: EmailStr = Field(..., example="new@example.com")
    name: str = Field(..., example="newUser")
    phoneNum: str = Field(..., example="010-1234-5678")
    address: str = Field(..., example="Seoul, South Korea")

class LoginRequest(BaseModel):
    id: str = Field(..., min_length=3, example="user")
    password: str = Field(..., min_length=6, example="user123")

class TokenRefreshRequest(BaseModel):
    refresh_token: str = Field(..., example="eyJhbGciOiJIUzI1...")

# Response Models 
class TokenData(BaseModel):
    access_token: str = Field(..., example="eyJhbGciOiJ...")
    refresh_token: str = Field(..., example="eyJhbGciOiJ...")

class RegisterResponse(ResponseBase[None]):
    """회원가입 응답 모델"""
    pass

class LoginResponse(ResponseBase[TokenData]):
    """로그인 응답 모델"""
    pass

class TokenRefreshResponse(ResponseBase[TokenData]):
    """액세스 토큰 재발급 응답 모델"""
    pass

class LogoutResponse(ResponseBase[None]):
    """로그아웃 응답 모델"""
    pass