from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from datetime import datetime, timedelta
import jwt
import logging
from typing import Optional, List, Tuple
from fastapi import Depends
from app.core.config import settings
from app.core.redis import redis_handler
from app.utils.exceptions import ForbiddenError, JWTError, UnauthorizedError
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class JWTPayload(BaseModel):
    """JWT 페이로드 모델"""
    exp: datetime = Field(..., description="토큰 만료 시간")
    user_pk: int = Field(..., description="사용자 PK")
    role: str = Field(..., description="사용자 역할")
    type: str = Field(..., description="토큰 유형 (access / refresh)")

    @classmethod
    def from_dict(cls, payload: dict) -> "JWTPayload":
        return cls(**payload)

    def to_dict(self) -> dict:
        return self.dict()

class JWTHandler:
    def __init__(self):
        self.settings = settings
        self.bearer_scheme = HTTPBearer()
        self.fernet = settings.fernet_instance
        logger.info("✅ JWTHandler 초기화 완료")

    def encrypt_role(self, role: str) -> str:
        try:
            return self.fernet.encrypt(role.encode()).decode()
        except Exception as e:
            raise JWTError(
                message="Failed to encrypt role",
                detail={"error": str(e)}
            )

    def decrypt_role(self, encrypted_role: str) -> str:
        try:
            return self.fernet.decrypt(encrypted_role.encode()).decode()
        except Exception as e:
            raise JWTError(
                message="Failed to decrypt role",
                detail={"error": str(e)}
            )

    def create_token(self, user_pk: int, role: str) -> Tuple[str, str]:
        encrypted_role = self.encrypt_role(role)
        self.delete_refresh_token(user_pk, role)  # 기존 리프레시 토큰 삭제
        refresh_token = self._create_refresh_token(user_pk, role)
        self.save_refresh_token(user_pk, role, refresh_token)
        access_token = self._create_access_token(user_pk, encrypted_role)
        return access_token, refresh_token

    def _create_access_token(self, user_pk: int, encrypted_role: str) -> str:
        try:
            expires_at = datetime.now() + timedelta(seconds=self.settings.ACCESS_TOKEN_EXPIRE_SECONDS)
            payload = JWTPayload(
                exp=expires_at,
                user_pk=user_pk,
                role=encrypted_role,
                type="access"
            ).to_dict()
            return jwt.encode(
                payload,
                self.settings.JWT_SECRET_KEY,
                algorithm=self.settings.JWT_ALGORITHM
            )
        except Exception as e:
            raise JWTError(
                message="Failed to create access token",
                detail={"error": str(e)}
            )

    def _create_refresh_token(self, user_pk: int, role: str) -> str:
        try:
            expires_at = datetime.now() + timedelta(seconds=self.settings.REFRESH_TOKEN_EXPIRE_SECONDS)
            payload = JWTPayload(
                exp=expires_at,
                user_pk=user_pk,
                role=role,
                type="refresh"
            ).to_dict()
            return jwt.encode(
                payload,
                self.settings.JWT_SECRET_KEY,
                algorithm=self.settings.JWT_ALGORITHM
            )
        except Exception as e:
            raise JWTError(
                message="Failed to create refresh token",
                detail={"error": str(e)}
            )

    def save_refresh_token(self, user_pk: int, role: str, refresh_token: str):
        redis_key = f"user:{role}:{user_pk}:refresh_token"
        redis_handler.setex(
            redis_key,
            refresh_token,
            self.settings.REFRESH_TOKEN_EXPIRE_SECONDS
        )

    def get_refresh_token(self, user_pk: int, role: str) -> Optional[str]:
        redis_key = f"user:{role}:{user_pk}:refresh_token"
        return redis_handler.get(redis_key)

    def delete_refresh_token(self, user_pk: int, role: str):
        redis_key = f"user:{role}:{user_pk}:refresh_token"
        if not redis_handler.delete(redis_key):
            logger.warning(f"⚠️ Redis에서 리프레시 토큰 삭제 실패: {redis_key}")

    def refresh_access_token(self, refresh_token: str) -> Tuple[str, str]:
        try:
            payload = jwt.decode(
                refresh_token,
                self.settings.JWT_SECRET_KEY,
                algorithms=[self.settings.JWT_ALGORITHM]
            )
            
            if payload.get("type") != "refresh":
                raise UnauthorizedError(
                    message="Invalid token type",
                    detail={"required": "refresh", "received": payload.get("type")}
                )

            user_pk = payload["user_pk"]
            role = payload["role"]
            stored_refresh_token = self.get_refresh_token(user_pk, role)

            if stored_refresh_token != refresh_token:
                raise UnauthorizedError(
                    message="Invalid refresh token",
                    detail={"error": "Stored token does not match provided token"}
                )

            self.delete_refresh_token(user_pk, role)
            new_refresh_token = self._create_refresh_token(user_pk, role)
            self.save_refresh_token(user_pk, role, new_refresh_token)
            new_access_token = self._create_access_token(user_pk, self.encrypt_role(role))

            return new_access_token, new_refresh_token

        except jwt.ExpiredSignatureError:
            raise UnauthorizedError(message="Refresh token has expired")
        except jwt.InvalidTokenError as e:
            raise UnauthorizedError(
                message="Invalid refresh token",
                detail={"error": str(e)}
            )

    async def validate_token(self, token: str, allowed_roles: Optional[List[str]] = None) -> JWTPayload:
        if not token:
          raise UnauthorizedError(
              message="Token is required",
              detail={"error": "No token provided"}
          )
        try:
            decoded_payload = jwt.decode(
                token,
                self.settings.JWT_SECRET_KEY,
                algorithms=[self.settings.JWT_ALGORITHM]
            )
            payload = JWTPayload.from_dict(decoded_payload)

            if payload.type != "access":
                raise UnauthorizedError(
                    message="Invalid token type",
                    detail={
                        "required": "access",
                        "received": payload.type
                    }
                )

            try:
                payload.role = self.decrypt_role(payload.role)
            except Exception as e:
                raise UnauthorizedError(
                    message="Invalid role encryption",
                    detail={"error": str(e)}
                )

            if allowed_roles and payload.role not in allowed_roles:
                raise ForbiddenError(
                    message="Permission denied",
                    detail={
                        "user_role": payload.role,
                        "allowed_roles": allowed_roles
                    }
                )

            return payload

        except jwt.ExpiredSignatureError:
            raise UnauthorizedError(
                message="Token has expired",
                detail={"error": "Token expiration time has passed"}
            )
        except jwt.InvalidSignatureError:
            raise UnauthorizedError(
                message="Token signature is invalid",
                detail={"error": "Token has been tampered with"}
            )
        except jwt.DecodeError:
            raise UnauthorizedError(
                message="Token is malformed",
                detail={"error": "Invalid token format"}
            )
        except jwt.InvalidTokenError as e:
            raise UnauthorizedError(
                message="Invalid token",
                detail={"error": str(e)}
            )
        except Exception as e:
            raise e

    def jwt_auth_dependency(self, allowed_roles: Optional[List[str]] = None):
        """FastAPI 의존성 함수: JWT 인증 및 역할 검증"""
        bearer = HTTPBearer(auto_error=False)  # auto_error를 False로 설정

        async def dependency(auth: Optional[HTTPAuthorizationCredentials] = Depends(bearer)):
            if not auth:
                raise UnauthorizedError(
                    message="Authentication required",
                    detail={
                        "error": "Authorization header is missing"
                    }
                )
                
            try:
                return await self.validate_token(auth.credentials, allowed_roles)
            except Exception as e:
                if isinstance(e, (UnauthorizedError, ForbiddenError)):
                    raise e
                raise UnauthorizedError(
                    message="Invalid token",
                    detail={"error": str(e)}
                )

        return dependency

jwt_handler = JWTHandler()