from fastapi import HTTPException
from app.schemas.user.login import UserLoginRequest, UserLoginResponse
from app.dummy_data import dummy_users
from app.utils.bcrypt import verify_password
from app.utils.jwt import create_jwt_token


class UserLoginService:
    """ 사용자 로그인 서비스 클래스 """

    @staticmethod
    def login_user(user: UserLoginRequest) -> UserLoginResponse:
        """ 사용자 로그인을 처리합니다 """

        errors = []

        # 사용자 ID 조회
        matched_user = next((u for u in dummy_users if u["userId"] == user.userId), None)

        if not matched_user:
            errors.append({"field": "userId", "message": "User ID does not exist"})

        # 비밀번호 검증
        elif not verify_password(user.userPassword, str(matched_user["userPassword"])):
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
            token=token,
            errors=[] 
        )
