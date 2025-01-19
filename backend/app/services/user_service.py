from fastapi import HTTPException
from app.models.user import UserRegisterRequest, UserRegisterResponse
from app.dummy_data import dummy_users

class UserService:
    """
    회원가입 관련 비즈니스 로직을 처리하는 서비스 클래스
    """

    @staticmethod
    def register_user(user: UserRegisterRequest) -> UserRegisterResponse:
        """
        회원가입 기능을 수행하는 메서드

        주어진 사용자 정보를 검증하고, 문제가 없으면 새로운 계정을 생성합니다.

        Args:
            user (UserRegisterRequest): 회원가입 요청 데이터

        Returns:
            UserRegisterResponse: 회원가입 응답 데이터

        Raises:
            HTTPException: 회원가입 실패 시 예외 발생

        예제 응답 (실패 시):
        ```
        HTTP 400 Bad Request
        {
            "resultCode": "FAILURE",
            "message": "User registration failed",
            "errors": [
                {"field": "userEmail", "message": "Email is required"}
            ]
        }
        ```
        """
        errors = []

        # 중복 체크
        if any(u["userId"] == user.userId for u in dummy_users):
            errors.append({"field": "userId", "message": "User ID already exists"})
        
        if any(u["userEmail"] == user.userEmail for u in dummy_users):
            errors.append({"field": "userEmail", "message": "Email is already registered"})
        
        # 필수 필드 검증
        if not user.userEmail.strip():
            errors.append({"field": "userEmail", "message": "Email is required"})

        # 에러가 있다면 예외 발생
        if errors:
            raise HTTPException(
                status_code=400,
                detail={
                    "resultCode": "FAILURE",
                    "message": "User registration failed",
                    "errors": errors
                }
            )

        # 새로운 유저 추가
        new_user = user.dict()
        dummy_users.append(new_user)

        return UserRegisterResponse(resultCode="SUCCESS", message="User registered successfully")
