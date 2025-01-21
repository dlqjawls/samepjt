from fastapi import HTTPException
from app.schemas.user.login import UserLoginRequest, UserLoginResponse
from app.dummy_data import dummy_users
from app.utils.bcrypt import verify_password
from app.utils.jwt import create_jwt_token


class UserLoginService:
    """🛠️ 로그인 관련 비즈니스 로직을 처리하는 서비스 클래스"""

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
