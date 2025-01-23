from fastapi import HTTPException
from sqlmodel import Session
from app.crud.user import get_user_by_id
from app.api.schemas.user.login import UserLoginRequest, UserLoginResponse
from app.utils.bcrypt import verify_password
from app.utils.jwt import create_token

class UserLoginService:

    @staticmethod
    def login_user(session: Session, user_request: UserLoginRequest) -> UserLoginResponse:

        errors = []
        # userId로 DB조회 (CRUD 호출)
        matched_user = get_user_by_id(session, user_request.userId)

        if not matched_user:
            errors.append({"field": "userId", "message": "User ID does not exist"})
        else:
            # 비밀번호 검증 (bcrypt)
            if not verify_password(user_request.userPassword, matched_user.userPassword):
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
        access_token, refresh_token = create_token(
            matched_user.userPK,
            role="user"
        )

        return UserLoginResponse(
            resultCode="SUCCESS",
            message="Login successful",
            accessToken=access_token,
            refreshToken=refresh_token,
            errors=[]
        )