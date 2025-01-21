from pydantic import BaseModel, Field
from typing import List, Optional


class AdminLoginRequest(BaseModel):
    """로그인 요청 모델"""
    adminId: str = Field(..., min_length=3, example="admin")
    adminPassword: str = Field(..., min_length=6, example="admin123")


class AdminLoginResponse(BaseModel):
    """로그인 응답 모델"""
    resultCode: str = Field(..., example="SUCCESS")
    message: str = Field(..., example="Login successful")
    token: Optional[str] = Field(None, example="eyJhbGciOi...")
    errors: Optional[List[str]] = Field(None, example=["Incorrect password"])
