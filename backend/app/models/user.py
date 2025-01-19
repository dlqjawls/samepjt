from pydantic import BaseModel, EmailStr
from typing import Union, List

class UserRegisterRequest(BaseModel):
    """
    회원가입 요청 모델

    Attributes:
        userId (str): 사용자의 고유 아이디
        userPassword (str): 사용자의 비밀번호
        userEmail (EmailStr): 이메일 주소 (유효한 이메일 형식 필수)
        userName (str): 사용자 이름
        userPhoneNum (str): 사용자 전화번호
        userAddress (str): 사용자 주소
    """
    userId: str
    userPassword: str
    userEmail: EmailStr
    userName: str
    userPhoneNum: str
    userAddress: str

class UserRegisterResponse(BaseModel):
    """
    회원가입 응답 모델

    Attributes:
        resultCode (str): 응답 코드 ("SUCCESS" 또는 "FAILURE")
        message (str): 응답 메시지
        errors (Union[List, None]): 오류 목록 (회원가입 실패 시 포함됨)
    """
    resultCode: str
    message: str
    errors: Union[List, None] = None  # 수정된 부분

class UserLoginRequest(BaseModel):
    """
    로그인 요청 모델

    Attributes:
        userId (str): 사용자의 아이디
        userPassword (str): 사용자의 비밀번호
    """
    userId: str
    userPassword: str

class UserLoginResponse(BaseModel):
    """
    로그인 응답 모델

    Attributes:
        resultCode (str): 응답 코드 ("SUCCESS" 또는 "FAILURE")
        message (str): 응답 메시지
        token (Union[str, None]): 로그인 성공 시 JWT 토큰 반환
        errors (Union[List, None]): 로그인 실패 시 오류 목록 포함
    """
    resultCode: str
    message: str
    token: Union[str, None] = None
    errors: Union[List, None] = None