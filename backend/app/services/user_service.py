from fastapi import HTTPException
from app.models.user import UserRegisterRequest, UserRegisterResponse, UserLoginRequest, UserLoginResponse
from app.dummy_data import dummy_users
from app.utils.bcrypt import hash_password, verify_password
from app.utils.jwt import create_jwt_token

class UserService:
    """
    회원가입 및 로그인 관련 비즈니스 로직을 처리하는 서비스 클래스
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
        
        # 비밀번호 해싱 후 저장
        hashed_password = hash_password(user.userPassword)  # 🔹 bcrypt 유틸리티 적용

        # 새로운 유저 추가
        new_user = user.dict()
        new_user["userPassword"] = hashed_password  # 해싱된 비밀번호 저장
        dummy_users.append(new_user)

        return UserRegisterResponse(resultCode="SUCCESS", message="User registered successfully")

    @staticmethod
    def login_user(user: UserLoginRequest) -> UserLoginResponse:
        """
        로그인 기능

        주어진 사용자 정보를 검증하고, 로그인 성공 시 JWT 토큰을 생성합니다. #TODO: JWT 토큰 생성

        Args:
            user (UserLoginRequest): 로그인 요청 데이터

        Returns:
            UserLoginResponse: 로그인 응답 데이터

        Raises:
            HTTPException: 로그인 실패 시 예외 발생
        """
        errors = []

        # 사용자 조회
        matched_user = next((u for u in dummy_users if u["userId"] == user.userId), None)

        if not matched_user:
            errors.append({"field": "userId", "message": "User ID does not exist"})

        elif not verify_password(user.userPassword, matched_user["userPassword"]):  # 🔹 bcrypt 유틸리티 적용
            errors.append({"field": "userPassword", "message": "Incorrect password"})

        if errors:
            raise HTTPException(
                status_code=401,
                detail={
                    "resultCode": "FAILURE",
                    "message": "Login failed",
                    "errors": errors
                }
            )


        # JWT 토큰 생성
        token = create_jwt_token(user.userId, role="user")  # 기본 역할 "user"

        return UserLoginResponse(
            resultCode="SUCCESS",
            message="Login successful",
            token= token
        )
