from fastapi import HTTPException
from app.models.user import User
from app.api.schemas.user.login import UserLoginRequest, UserLoginResponse
from app.core.database import get_session
from app.utils.bcrypt import verify_password
from app.utils.jwt import create_token
from sqlmodel import select

class UserLoginService:
    """ 사용자 로그인 서비스 클래스 """

    @staticmethod
    def login_user(user: UserLoginRequest) -> UserLoginResponse:
        """ 사용자 로그인을 처리합니다 """
        with get_session() as session:
            errors = []

            # 사용자 ID 조회
            statement = select(User).where(User.userId == user.userId)
            matched_user = session.exec(statement).first()

            if not matched_user:
                errors.append({"field": "userId", "message": "User ID does not exist"})

            # 비밀번호 검증
            elif not verify_password(user.userPassword, matched_user.userPassword):
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

            # JWT 토큰 생성 및 저장
            access_token, refresh_token = create_token(matched_user.userPK, role="user")

            return UserLoginResponse(
                resultCode="SUCCESS",
                message="Login successful",
                accessToken=access_token,
                refreshToken=refresh_token,
                errors=[]
            )