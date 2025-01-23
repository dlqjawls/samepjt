from pydantic import BaseModel, EmailStr, Field


class UserSchema(BaseModel):
    """사용자 정보 모델"""
    userId: str = Field(..., example="john_doe")
    userPassword: str = Field(..., example="securepassword")
    userEmail: EmailStr = Field(..., example="john@example.com")
    userName: str = Field(..., example="John Doe")
    userPhoneNum: str = Field(..., example="010-1234-5678")
    userAddress: str = Field(..., example="123 Main St, City, Country")
