from pydantic import BaseModel, EmailStr
from typing import Union, List

class UserRegisterRequest(BaseModel):
    userId: str
    userPassword: str
    userEmail: EmailStr
    userName: str
    userPhoneNum: str
    userAddress: str

class UserRegisterResponse(BaseModel):
    resultCode: str
    message: str
    errors: Union[List, None] = None  # 수정된 부분
