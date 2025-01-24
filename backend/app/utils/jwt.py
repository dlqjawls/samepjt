# app/core/jwt_handler.py
from cryptography.fernet import Fernet
import jwt
import datetime
from typing import Optional, Dict, Tuple, List
import os
from app.core.redis_config import redis_config
from fastapi import Request, HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseSettings

class JWTSettings(BaseSettings):
    """JWT 설정 클래스"""
    SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "default_secret_key")
    ROLE_ENCRYPTION_KEY: str = os.getenv("ROLE_ENCRYPTION_KEY", Fernet.generate_key().decode())
    HASH_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 600   # 10분
    REFRESH_TOKEN_EXPIRE_SECONDS: int = 1200 # 20분


class JWTHandler:
    """JWT 토큰 핸들러"""
    def __init__(self):
        self.settings = JWTSettings()
        self.fernet = Fernet(self.settings.ROLE_ENCRYPTION_KEY.encode())
        self.redis_client = redis_config()
        self.bearer_scheme = HTTPBearer()

    def encrypt_role(self, role: str) -> str:
        """역할 정보 암호화"""
        return self.fernet.encrypt(role.encode()).decode()

    def decrypt_role(self, encrypted_role: str) -> str:
        """암호화된 역할 정보 복호화"""
        return self.fernet.decrypt(encrypted_role.encode()).decode()

    def create_token(self, user_pk: int, role: str) -> Tuple[str, str]:
        """액세스 토큰과 리프레시 토큰 생성 (리프레시 토큰 중복 저장 방지)"""
        encrypted_role = self.encrypt_role(role)
        
        # 기존 리프레시 토큰 무효화 (기존 사용자 로그인 시)
        self.delete_refresh_token(user_pk)

        # 새로운 리프레시 토큰 생성
        refresh_token = self._create_refresh_token(user_pk)
        self.save_refresh_token(user_pk, refresh_token)

        # 액세스 토큰 생성
        access_token = self._create_access_token(user_pk, encrypted_role)

        return access_token, refresh_token


    def _create_access_token(self, user_pk: int, encrypted_role: str) -> str:
        """액세스 토큰 생성"""
        expires_at = datetime.datetime.utcnow() + datetime.timedelta(seconds=self.settings.ACCESS_TOKEN_EXPIRE_SECONDS)

        payload = {
            "exp": expires_at,
            "user_pk": user_pk,
            "role": encrypted_role,
            "type": "access"
        }
        return jwt.encode(payload, self.settings.SECRET_KEY, algorithm=self.settings.HASH_ALGORITHM)

    def _create_refresh_token(self, user_pk: int) -> str:
        """리프레시 토큰 생성"""
        expires_at = datetime.datetime.utcnow() + datetime.timedelta(seconds=self.settings.REFRESH_TOKEN_EXPIRE_SECONDS)

        payload = {
            "exp": expires_at,
            "user_pk": user_pk,
            "type": "refresh"
        }
        return jwt.encode(payload, self.settings.SECRET_KEY, algorithm=self.settings.HASH_ALGORITHM)

    def save_refresh_token(self, user_pk: int, refresh_token: str):
        """리프레시 토큰을 Redis에 저장"""
        redis_key = f"user:{user_pk}:refresh_token"
        self.redis_client.setex(key=redis_key, value=refresh_token, ttl=self.settings.REFRESH_TOKEN_EXPIRE_SECONDS)

    def get_refresh_token(self, user_pk: int) -> Optional[str]:
        """Redis에서 리프레시 토큰을 가져오기"""
        redis_key = f"user:{user_pk}:refresh_token"
        token = self.redis_client.get(redis_key)
        return token if token else None

    def delete_refresh_token(self, user_pk: int):
        """리프레시 토큰 삭제 (로그아웃)"""
        redis_key = f"user:{user_pk}:refresh_token"
        self.redis_client.delete(redis_key)

    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """리프레시 토큰을 검증하고 새 액세스 토큰 발급"""
        try:
            payload = jwt.decode(refresh_token, self.settings.SECRET_KEY, algorithms=[self.settings.HASH_ALGORITHM])
            if payload.get("type") != "refresh":
                raise HTTPException(status_code=401, detail="Invalid token type")

            user_pk = payload["user_pk"]
            stored_refresh_token = self.get_refresh_token(user_pk)

            if stored_refresh_token != refresh_token:
                raise HTTPException(status_code=401, detail="Invalid refresh token")

            # 새로운 액세스 토큰 생성
            return self._create_access_token(user_pk, self.encrypt_role("user"))

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Refresh token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

    async def validate_token(self, token: str, allowed_roles: Optional[List[str]] = None) -> Dict:
        """JWT 토큰 검증 및 역할(Role) 검증"""
        try:
            payload = jwt.decode(token, self.settings.SECRET_KEY, algorithms=[self.settings.HASH_ALGORITHM])
            if payload.get("type") != "access":
                raise HTTPException(status_code=401, detail="Invalid token type")

            payload["role"] = self.decrypt_role(payload["role"])

            # 역할(Role) 검증 수행
            if allowed_roles:
                if payload["role"] not in allowed_roles:
                    raise HTTPException(status_code=403, detail="Permission denied")

            return payload

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

    def jwt_auth_dependency(self, allowed_roles: Optional[List[str]] = None):
        """
        FastAPI 의존성 함수(Dependency)를 반환.
        allowed_roles가 주어지면 해당 권한만 접근 가능하도록 검증.
        없거나 빈 리스트라면 유효한 토큰이면 모두 접근 가능.
        """
        async def _validate_token(credentials: HTTPAuthorizationCredentials = Depends(self.bearer_scheme)):
            # bearer_scheme을 통해 Authorization 헤더 내의 JWT를 가져온다.
            token = credentials.credentials
            # 토큰 검증 로직 호출
            payload = await self.validate_token(token, allowed_roles if allowed_roles else None)
            return payload

        return _validate_token


# JWT 핸들러 인스턴스 생성
jwt_handler = JWTHandler()
