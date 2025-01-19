from fastapi import HTTPException
from app.models.user import UserRegisterRequest, UserRegisterResponse
from app.dummy_data import dummy_users

class UserService:
    @staticmethod
    def register_user(user: UserRegisterRequest) -> UserRegisterResponse:
        errors = []

        # 중복 체크
        if any(u["userId"] == user.userId for u in dummy_users):
            errors.append({"field": "userId", "message": "User ID already exists"})
        
        if any(u["userEmail"] == user.userEmail for u in dummy_users):
            errors.append({"field": "userEmail", "message": "Email is already registered"})
        
        # 필수 필드 검증
        if not user.userEmail.strip():
            errors.append({"field": "userEmail", "message": "Email is required"})

        # 에러가 있다면 반환
        if errors:
            raise HTTPException(
                status_code=400,
                detail={
                    "resultCode": "FAILURE",
                    "message": "User registration failed",
                    "errors": errors
                }
            )

        # 새 유저 저장
        new_user = user.dict()
        dummy_users.append(new_user)

        return UserRegisterResponse(resultCode="SUCCESS", message="User registered successfully")
