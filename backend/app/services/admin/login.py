from fastapi import HTTPException, status
from sqlmodel import Session
from app.crud.admin import get_admin_by_id
from app.api.schemas.admin.login import AdminLoginRequest, AdminLoginResponse
from app.utils.bcrypt import verify_password
from app.utils.jwt import jwt_handler 

class AdminLoginService:

    @staticmethod
    def login_admin(session: Session, admin_request: AdminLoginRequest) -> AdminLoginResponse:
        errors = []

        # adminId로 DB 조회
        matched_admin = get_admin_by_id(session, admin_request.adminId)

        if matched_admin is None:
            errors.append({"field": "adminId", "message": "Admin ID does not exist"})
        elif not verify_password(admin_request.adminPassword, matched_admin.adminPassword):
            errors.append({"field": "adminPassword", "message": "Incorrect password"})

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
        access_token, refresh_token = jwt_handler.create_token(
            matched_admin.adminPK, 
            role=str(matched_admin.role)
        )

        return AdminLoginResponse(
            resultCode="SUCCESS",
            message="Login successful",
            accessToken=access_token,
            refreshToken=refresh_token,
            errors=[]
        )