from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional


class UserRegisterRequest(BaseModel):
    """회원가입 요청 모델"""
    userId: str = Field(..., min_length=3, example="testUser")
    userPassword: str = Field(..., min_length=6, example="securePassword123")
    userEmail: EmailStr = Field(..., example="test@example.com")
    userName: str = Field(..., example="Test User")
    userPhoneNum: str = Field(..., example="010-1234-5678")
    userAddress: str = Field(..., example="Seoul, South Korea")


class UserRegisterResponse(BaseModel):
    """회원가입 응답 모델"""
    resultCode: str = Field(..., example="SUCCESS")
    message: str = Field(..., example="User registered successfully")
    errors: Optional[List[str]] = Field(None, example=["User ID already exists"])


class UserLoginRequest(BaseModel):
    """로그인 요청 모델"""
    userId: str = Field(..., min_length=3, example="testUser")
    userPassword: str = Field(..., min_length=6, example="securePassword123")


class UserLoginResponse(BaseModel):
    """로그인 응답 모델"""
    resultCode: str = Field(..., example="SUCCESS")
    message: str = Field(..., example="Login successful")
    token: Optional[str] = Field(None, example="eyJhbGciOi...")
    errors: Optional[List[str]] = Field(None, example=["Incorrect password"])

class UserSchema(BaseModel):
    """사용자 정보 모델"""
    userId: str = Field(..., example="john_doe")
    userPassword: str = Field(..., example="securepassword")
    userEmail: EmailStr = Field(..., example="john@example.com")
    userName: str = Field(..., example="John Doe")
    userPhoneNum: str = Field(..., example="010-1234-5678")
    userAddress: str = Field(..., example="123 Main St, City, Country")