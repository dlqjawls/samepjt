from fastapi import HTTPException
from app.schemas.admin.login import AdminLoginRequest, AdminLoginResponse
from app.dummy_data import dummy_admins
from app.utils.bcrypt import verify_password
from app.utils.jwt import create_access_token, create_refresh_token


class AdminLoginService:
    """ 관리자 로그인 서비스 클래스 """

    @staticmethod
    def login_admin(admin: AdminLoginRequest) -> AdminLoginResponse:
        """ 관리자 로그인을 처리합니다 """

        errors = []

        # 관리자 ID 조회
        matched_user = next((u for u in dummy_admins if u["adminId"] == admin.adminId), None)

        if not matched_user:
            errors.append({"field": "adminId", "message": "Admin ID does not exist"})

        # 비밀번호 검증
        elif not verify_password(admin.adminPassword, str(matched_user["adminPassword"])):
            errors.append({"field": "adminPassword", "message": "Incorrect password"})

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
        access_token = create_access_token(matched_user["adminPK"], role=str(matched_user["role"]))
        refresh_token = create_refresh_token(matched_user["adminPK"])

        return AdminLoginResponse(
            resultCode="SUCCESS",
            message="Login successful",
            accessToken=access_token,
            refreshToken=refresh_token,
            errors=[]
        )
