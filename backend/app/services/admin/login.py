from fastapi import HTTPException
from sqlmodel import Session
from app.crud.admin import get_admin_by_admin_id
from app.api.schemas.admin.login import AdminLoginRequest, AdminLoginResponse
from app.utils.bcrypt import verify_password
from app.utils.jwt import create_token

class AdminLoginService:

    @staticmethod
    def login_admin(session: Session, admin_request: AdminLoginRequest) -> AdminLoginResponse:

        errors = []
        # adminId로 DB조회 (CRUD 호출)
        matched_admin = get_admin_by_admin_id(session, admin_request.adminId)

        if not matched_admin:
            errors.append({"field": "adminId", "message": "Admin ID does not exist"})
        else:
            # 비밀번호 검증 (bcrypt)
            if not verify_password(admin_request.adminPassword, matched_admin.adminPassword):
                errors.append({"field": "adminPassword", "message": "Incorrect password"})

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
