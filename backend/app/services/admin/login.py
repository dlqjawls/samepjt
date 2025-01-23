from fastapi import HTTPException
from app.models.admin import Admin
from app.schemas.admin.login import AdminLoginRequest, AdminLoginResponse
from app.core.database import get_session
from app.utils.bcrypt import verify_password
from app.utils.jwt import create_access_token, create_refresh_token
from sqlmodel import select

class AdminLoginService:
    """ 관리자 로그인 서비스 클래스 """

    # 토큰 저장을 위한 딕셔너리
    # TODO: Redis 저장 방식으로 변경
    token_store: dict[int, dict[str, str]] = {}

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

            # JWT 토큰 생성
            access_token = create_access_token(matched_user.adminPK, role=str(matched_user.role))
            refresh_token = create_refresh_token(matched_user.adminPK)

            # 토큰 저장
            AdminLoginService.token_store[matched_user.adminPK] = {
                "access_token": access_token,
                "refresh_token": refresh_token
            }

            return AdminLoginResponse(
                resultCode="SUCCESS",
                message="Login successful",
                accessToken=access_token,
                refreshToken=refresh_token,
                errors=[]
            )