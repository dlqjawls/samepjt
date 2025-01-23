from fastapi import HTTPException
from app.models.admin import Admin
from app.schemas.admin.login import AdminLoginRequest, AdminLoginResponse
from app.core.database import get_session
from app.utils.bcrypt import verify_password
from app.utils.jwt import create_token
from sqlmodel import select

class AdminLoginService:
    """ 관리자 로그인 서비스 클래스 """

    @staticmethod
    def login_admin(admin: AdminLoginRequest) -> AdminLoginResponse:
        """ 관리자 로그인을 처리합니다 """

        errors = []

        # 관리자 ID 조회
        with get_session() as session:
            statement = select(Admin).where(Admin.adminId == admin.adminId)
            matched_user = session.exec(statement).first()

            if not matched_user:
                errors.append({"field": "adminId", "message": "Admin ID does not exist"})

            # 비밀번호 검증
            elif not verify_password(admin.adminPassword, matched_user.adminPassword):
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

            # JWT 토큰 생성 및 저장
            access_token, refresh_token = create_token(matched_user.adminPK, role=str(matched_user.role))

            return AdminLoginResponse(
                resultCode="SUCCESS",
                message="Login successful",
                accessToken=access_token,
                refreshToken=refresh_token,
                errors=[]
            )