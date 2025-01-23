from pydantic import BaseModel, Field
from typing import List, Optional


class UserLoginRequest(BaseModel):
    """로그인 요청 모델"""
    userId: str = Field(..., min_length=3, example="test123")
    userPassword: str = Field(..., min_length=6, example="test123")


class UserLoginResponse(BaseModel):
    """로그인 응답 모델"""
    resultCode: str = Field(..., example="SUCCESS")
    message: str = Field(..., example="Login successful")
    accessToken: str = Field(..., example="eyJhbGciOiJ...")
    refreshToken: str = Field(..., example="eyJhbGciOiJ...")
    errors: Optional[List[str]] = Field(None, example=["Incorrect password"])
