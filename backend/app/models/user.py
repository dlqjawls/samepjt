from pydantic import BaseModel, Field, EmailStr
from typing import Union, List


class UserRegisterRequest(BaseModel):
    """회원가입 요청 모델"""
    userId: str = Field(..., min_length=3, description="최소 3자 이상")
    userPassword: str = Field(..., min_length=6, description="최소 6자 이상")
    userEmail: EmailStr
    userName: str = Field(..., min_length=1)
    userPhoneNum: str = Field(..., min_length=1)
    userAddress: str = Field(..., min_length=1)


class UserRegisterResponse(BaseModel):
    """회원가입 응답 모델"""
    resultCode: str
    message: str
    errors: Union[List, None] = None


class UserLoginRequest(BaseModel):
    """로그인 요청 모델"""
    userId: str = Field(..., min_length=3, description="최소 3자 이상")
    userPassword: str = Field(..., min_length=6, description="최소 6자 이상")


class UserLoginResponse(BaseModel):
    """로그인 응답 모델"""
    resultCode: str
    message: str
    token: Union[str, None] = None
    errors: Union[List, None] = None
