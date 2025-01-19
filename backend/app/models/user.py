from pydantic import BaseModel, EmailStr

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
    errors: list | None = None
