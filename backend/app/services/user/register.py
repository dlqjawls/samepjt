from fastapi import HTTPException
from app.schemas.user.register import UserRegisterRequest, UserRegisterResponse
from app.dummy_data import dummy_users
from app.utils.bcrypt import hash_password


class UserRegisterService:
    """🛠️ 회원가입 관련 비즈니스 로직을 처리하는 서비스 클래스"""

    @staticmethod
    def register_user(user: UserRegisterRequest) -> UserRegisterResponse:
        """
        회원가입 기능

        - `userId` 및 `userEmail`은 중복될 수 없음
        - `userPassword`는 `bcrypt`를 사용하여 해싱하여 저장
        - 회원가입 성공 시 `SUCCESS` 메시지를 반환

        예외 발생 시:
        - 이미 존재하는 `userId` 또는 `userEmail`
        - 필수 입력값 누락 (예: 이메일이 빈 문자열일 경우)
        - `400 Bad Request` 응답 반환
        """
        errors = []

        # 중복 검사
        if any(u["userId"] == user.userId for u in dummy_users):
            errors.append({"field": "userId", "message": "User ID already exists"})
        
        if any(u["userEmail"] == user.userEmail for u in dummy_users):
            errors.append({"field": "userEmail", "message": "Email is already registered"})
        
        # 필수 입력값 검증
        if not user.userEmail.strip():
            errors.append({"field": "userEmail", "message": "Email is required"})

        # 유효성 검사 실패 시 예외 발생
        if errors:
            raise HTTPException(
                status_code=400,
                detail={
                    "resultCode": "FAILURE",
                    "message": "User registration failed",
                    "errors": errors
                }
            )
        
        # 비밀번호 해싱 후 저장
        hashed_password = hash_password(user.userPassword)

        # 새로운 사용자 추가
        new_user = user.dict()
        new_user["userPassword"] = hashed_password
        dummy_users.append(new_user)

        return UserRegisterResponse(resultCode="SUCCESS", message="User registered successfully")
