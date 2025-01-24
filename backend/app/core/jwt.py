import base64
from cryptography.fernet import Fernet
import jwt
import datetime
from typing import Optional, Dict, Tuple, List
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings, logger
from app.core.redis import redis_handler 

class JWTHandler:
    """🔹 JWT 토큰 핸들러"""
    def __init__(self):
        self.settings = settings
        self.bearer_scheme = HTTPBearer()

        # 🔹 ROLE_ENCRYPTION_KEY 검증 (Base64 32바이트 체크)
        try:
            decoded_key = base64.urlsafe_b64decode(self.settings.ROLE_ENCRYPTION_KEY)
            if len(decoded_key) != 32:
                raise ValueError("ROLE_ENCRYPTION_KEY는 32 바이트 Base64 URL-Safe 문자열이어야 합니다.")
            self.fernet = Fernet(self.settings.ROLE_ENCRYPTION_KEY.encode())
        except Exception as e:
            raise ValueError(f"ROLE_ENCRYPTION_KEY가 올바르지 않습니다: {e}")

        logger.info("✅ JWTHandler 초기화 완료")

    def encrypt_role(self, role: str) -> str:
        return self.fernet.encrypt(role.encode()).decode()

    def decrypt_role(self, encrypted_role: str) -> str:
        return self.fernet.decrypt(encrypted_role.encode()).decode()

    def create_token(self, user_pk: int, role: str) -> Tuple[str, str]:
        encrypted_role = self.encrypt_role(role)

        # 기존 리프레시 토큰 삭제
        self.delete_refresh_token(user_pk, role)

        # 새로운 리프레시 토큰 생성 및 저장
        refresh_token = self._create_refresh_token(user_pk, role)
        self.save_refresh_token(user_pk, role, refresh_token)

        # 액세스 토큰 생성
        access_token = self._create_access_token(user_pk, encrypted_role)

        return access_token, refresh_token

    def _create_access_token(self, user_pk: int, encrypted_role: str) -> str:
        expires_at = datetime.datetime.utcnow() + datetime.timedelta(seconds=self.settings.ACCESS_TOKEN_EXPIRE_SECONDS)

        payload = {
            "exp": expires_at,
            "user_pk": user_pk,
            "role": encrypted_role,
            "type": "access"
        }
        return jwt.encode(payload, self.settings.SECRET_KEY, algorithm=self.settings.HASH_ALGORITHM)

    def _create_refresh_token(self, user_pk: int, role: str) -> str:
        expires_at = datetime.datetime.utcnow() + datetime.timedelta(seconds=self.settings.REFRESH_TOKEN_EXPIRE_SECONDS)

        payload = {
            "exp": expires_at,
            "user_pk": user_pk,
            "role": role,  
            "type": "refresh"
        }
        return jwt.encode(payload, self.settings.SECRET_KEY, algorithm=self.settings.HASH_ALGORITHM)

    def save_refresh_token(self, user_pk: int, role: str, refresh_token: str):
        redis_key = f"user:{role}:{user_pk}:refresh_token"
        if not redis_handler.setex(redis_key, refresh_token, self.settings.REFRESH_TOKEN_EXPIRE_SECONDS):
            raise HTTPException(status_code=500, detail="Redis에 리프레시 토큰 저장 실패")

    def get_refresh_token(self, user_pk: int, role: str) -> Optional[str]:
        redis_key = f"user:{role}:{user_pk}:refresh_token"
        return redis_handler.get(redis_key)

    def delete_refresh_token(self, user_pk: int, role: str):
        redis_key = f"user:{role}:{user_pk}:refresh_token"
        if not redis_handler.delete(redis_key):
            logger.warning(f"⚠️ Redis에서 리프레시 토큰 삭제 실패: {redis_key}")

    def refresh_access_token(self, refresh_token: str) -> Tuple[str, str]:
        try:
            # 리프레시 토큰 검증
            payload = jwt.decode(refresh_token, self.settings.SECRET_KEY, algorithms=[self.settings.HASH_ALGORITHM])
            if payload.get("type") != "refresh":
                raise HTTPException(status_code=401, detail="Invalid token type")

            user_pk = payload["user_pk"]
            role = payload["role"]  
            stored_refresh_token = self.get_refresh_token(user_pk, role)

            # 저장된 리프레시 토큰과 비교 (일치하지 않으면 무효화)
            if stored_refresh_token != refresh_token:
                raise HTTPException(status_code=401, detail="Invalid refresh token")

            # 기존 리프레시 토큰 삭제
            self.delete_refresh_token(user_pk, role)

            # 새로운 리프레시 토큰 생성
            new_refresh_token = self._create_refresh_token(user_pk, role)
            self.save_refresh_token(user_pk, role, new_refresh_token)

            # 새로운 액세스 토큰 생성
            new_access_token = self._create_access_token(user_pk, self.encrypt_role(role))

            return new_access_token, new_refresh_token

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Refresh token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

    async def validate_token(self, token: str, allowed_roles: Optional[List[str]] = None) -> Dict:
        try:
            payload = jwt.decode(token, self.settings.SECRET_KEY, algorithms=[self.settings.HASH_ALGORITHM])
            if payload.get("type") != "access":
                raise HTTPException(status_code=401, detail="Invalid token type")

            payload["role"] = self.decrypt_role(payload["role"])

            # 역할(Role) 검증 수행
            if allowed_roles and payload["role"] not in allowed_roles:
                raise HTTPException(status_code=403, detail="Permission denied")

            return payload

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

    def jwt_auth_dependency(self, allowed_roles: Optional[List[str]] = None):
        """FastAPI 의존성 함수: JWT 인증 및 역할 검증"""
        async def _validate_token(credentials: HTTPAuthorizationCredentials = Depends(self.bearer_scheme)):
            token = credentials.credentials
            payload = await self.validate_token(token, allowed_roles if allowed_roles else None)
            return payload

        return _validate_token


# JWT 핸들러 싱글톤 인스턴스
jwt_handler = JWTHandler()
