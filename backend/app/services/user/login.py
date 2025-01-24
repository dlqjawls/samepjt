from fastapi import HTTPException, status
from sqlmodel import Session
from app.crud.user import get_user_by_id
from app.api.schemas.user.login import UserLoginRequest, UserLoginResponse
from app.utils.bcrypt import verify_password
from app.core.jwt import jwt_handler 

class UserLoginService:

    @staticmethod
    def login_user(session: Session, user_request: UserLoginRequest) -> UserLoginResponse:
        errors = []

        # userId로 DB 조회
        matched_user = get_user_by_id(session, user_request.userId)

        if matched_user is None:
            errors.append({"field": "userId", "message": "User ID does not exist"})
        elif not verify_password(user_request.userPassword, matched_user.userPassword):
            errors.append({"field": "userPassword", "message": "Incorrect password"})

        if errors:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "resultCode": "FAILURE",
                    "message": "Login failed",
                    "errors": errors
                }
            )
        
        # JWT 토큰 생성
        if matched_user is not None and isinstance(matched_user.userPK, int):
            access_token, refresh_token = jwt_handler.create_token(
                matched_user.userPK, 
                role="user"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error: Invalid userPK"
            )

        return UserLoginResponse(
            resultCode="SUCCESS",
            message="Login successful",
            accessToken=access_token,
            refreshToken=refresh_token,
            errors=[]
        )