import logging
from typing import Optional, List
from sqlmodel import Session
from datetime import datetime

from app.db.models.user import User
from app.db.crud.user import user_crud
from app.db.crud.lut import role
from app.api.schemas import auth_schema
from app.utils.bcrypt import hash_password, verify_password
from app.core.jwt import JWTPayload, jwt_handler
from app.utils.handle_transaction import handle_transaction

from app.utils.exceptions import BadRequestError, DatabaseError, ForbiddenError, NotFoundError, UnauthorizedError

logger = logging.getLogger(__name__)

class AuthServiceUtils:
    """ 🎯 AuthService 공통 로직 """
    @staticmethod
    def validate_user_credentials(session: Session, user_id: str, password: str) -> User:
        user = user_crud.get_by_id(session, user_id)
        if not user or not verify_password(password, user.user_password):
            raise UnauthorizedError(
                message="Invalid credentials", 
                detail={
                    "error": "Invalid user ID or password",
                }
            )
        return user

    @staticmethod
    def get_user_role(session: Session, role_id: int) -> str:
        role_data = role.get_by_id(session, role_id)
        if not role_data:
            raise DatabaseError(
                message="User Role not found",
                detail={
                    "role_id": role_id
                }
            )
        return role_data.role_name


class AuthService:
    """
    회원가입, 로그인, 토큰갱신, 로그아웃
    """
    @staticmethod
    @handle_transaction
    def register(session: Session, register_req: auth_schema.RegisterRequest) -> auth_schema.RegisterResponse:
        """
        새 유저 등록
        """
        if user_crud.get_by_field(session, register_req.id, "user_id"):
            raise BadRequestError(
                message="User ID already exists",
                detail={
                    "id": register_req.id
                }
            )

        if user_crud.get_by_email(session, register_req.email):
            raise BadRequestError(
                message="Email is already exists",
                detail={
                    "email": register_req.email
                }
            )

        hashed_password = hash_password(register_req.password)
        new_user = User(
            user_id=register_req.id,
            user_password=hashed_password,
            user_email=register_req.email,
            user_name=register_req.name,
            user_phone_num=register_req.phoneNum,
            user_address=register_req.address,
            role_id=3,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        
        user_crud.create(session, new_user)

        return auth_schema.RegisterResponse.success(
            message="User registered successfully"
        )

    @staticmethod
    def login(session: Session, login_req: auth_schema.LoginRequest, allowed_roles: Optional[List[str]] = None) -> auth_schema.LoginResponse:
        matched_user = AuthServiceUtils.validate_user_credentials(session, login_req.id, login_req.password)
        role_name = AuthServiceUtils.get_user_role(session, matched_user.role_id)

        # user_pk가 None이면 DB 문제
        if matched_user.user_pk is None:
          raise DatabaseError(
              message="User primary key is missing",
              detail={
                  "user_id": matched_user.user_id,
                  "role_id": matched_user.role_id
              }
          )
          
        if allowed_roles and role_name not in allowed_roles:
            raise ForbiddenError(
                message="Permission denied",
                detail={
                    "error": "User does not have required role",
                    "allowed_roles": allowed_roles
                }
            )

        access_token, refresh_token = jwt_handler.create_token(matched_user.user_pk, role=role_name)

        return auth_schema.LoginResponse.success(
            message="Login successful",
            data=auth_schema.TokenData(
                access_token=access_token,
                refresh_token=refresh_token
            )
        )

    @staticmethod
    def refresh_access_token(refresh_req: auth_schema.TokenRefreshRequest) -> auth_schema.TokenRefreshResponse:
        new_access_token, new_refresh_token = jwt_handler.refresh_access_token(refresh_req.refresh_token)
        return auth_schema.TokenRefreshResponse.success(
            message="Token refreshed successfully",
            data=auth_schema.TokenData(
                access_token=new_access_token,
                refresh_token=new_refresh_token
            )
        )

    @staticmethod
    def logout(token_data: JWTPayload) -> auth_schema.LogoutResponse:
        user_pk = token_data.user_pk
        role_name = token_data.role

        if not user_pk or not role_name:
            raise UnauthorizedError(
                message="Invalid credentials",
                detail={
                    "error": "Authentication failed",
                    "error_type": "INVALID_CREDENTIALS"
                }
            ) 

        jwt_handler.delete_refresh_token(user_pk, role_name)
        return auth_schema.LogoutResponse.success(
            message="Successfully logged out"
        )