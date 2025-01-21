from fastapi import HTTPException
from app.schemas.user.register import UserRegisterRequest, UserRegisterResponse
from app.dummy_data import dummy_users
from app.utils.bcrypt import hash_password


class UserRegisterService:
    """ 사용자 회원가입 서비스 클래스 """

    @staticmethod
    def register_user(user: UserRegisterRequest) -> UserRegisterResponse:
        """ 새로운 사용자를 등록합니다 """

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

        return UserRegisterResponse(resultCode="SUCCESS", message="User registered successfully", errors=[])
