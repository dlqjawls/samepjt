from fastapi import HTTPException
from app.models.user import UserRegisterRequest, UserRegisterResponse, UserLoginRequest, UserLoginResponse
from app.dummy_data import dummy_users
from app.utils.bcrypt import hash_password, verify_password
from app.utils.jwt import create_jwt_token


class UserService:
    """🛠️ 회원가입 및 로그인 관련 비즈니스 로직을 처리하는 서비스 클래스"""

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

    @staticmethod
    def login_user(user: UserLoginRequest) -> UserLoginResponse:
        """
        로그인 기능

        - `userId`가 존재해야 하며, `userPassword`가 일치해야 로그인 가능
        - JWT 토큰이 생성되어 응답에 포함됨
        - 로그인 성공 시 `SUCCESS` 메시지를 반환

        예외 발생 시:
        - 존재하지 않는 `userId`
        - 잘못된 비밀번호 입력
        - `401 Unauthorized` 응답 반환
        """
        errors = []

        # 사용자 조회
        matched_user = next((u for u in dummy_users if u["userId"] == user.userId), None)

        if not matched_user:
            errors.append({"field": "userId", "message": "User ID does not exist"})

        elif not verify_password(user.userPassword, matched_user["userPassword"]):
            errors.append({"field": "userPassword", "message": "Incorrect password"})

        # 인증 실패 시 예외 발생
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
        token = create_jwt_token(user.userId, role="user")

        return UserLoginResponse(
            resultCode="SUCCESS",
            message="Login successful",
            token=token
        )
