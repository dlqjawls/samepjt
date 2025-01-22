from cryptography.fernet import Fernet
import jwt
import datetime
from typing import Optional
import os

# 환경 변수에서 SECRET_KEY 및 ROLE_ENCRYPTION_KEY 로드 (하드코딩 금지)
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "default_secret_key")  # JWT 서명용 비밀키
ROLE_ENCRYPTION_KEY = os.getenv("ROLE_ENCRYPTION_KEY", Fernet.generate_key().decode())  # 역할 암호화 키

HASH_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = 43200  # 12시간
REFRESH_TOKEN_EXPIRE_DAYS = 7  # 리프레시 토큰 만료 시간 (7일)

# 대칭키 암호화 도구 초기화
fernet = Fernet(ROLE_ENCRYPTION_KEY.encode())


def encrypt_role(role: str) -> str:
    """
    사용자 역할(role)을 암호화
    """
    return fernet.encrypt(role.encode()).decode()


def decrypt_role(encrypted_role: str) -> str:
    """
    암호화된 사용자 역할(role)을 복호화
    """
    return fernet.decrypt(encrypted_role.encode()).decode()


def create_access_token(userPK: int, role: str = "user", expires_delta: Optional[int] = None) -> str:
    """
    JWT 액세스 토큰 생성
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    expires = now + datetime.timedelta(seconds=expires_delta or ACCESS_TOKEN_EXPIRE_SECONDS)

    # 역할 암호화
    encrypted_role = encrypt_role(role)

    payload = {
        "userPK": userPK,
        "role": encrypted_role,  # 암호화된 역할 추가
        "iat": now,
        "exp": expires,
        "type": "access"
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=HASH_ALGORITHM)
    return token


def create_refresh_token(userPK: int) -> str:
    """
    리프레시 토큰 생성
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    expires = now + datetime.timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    payload = {
        "userPK": userPK,
        "iat": now,
        "exp": expires,
        "type": "refresh"
    }
    refresh_token = jwt.encode(payload, SECRET_KEY, algorithm=HASH_ALGORITHM)
    return refresh_token


def decode_jwt_token(token: str) -> dict:
    """
    JWT 토큰 검증 및 디코딩
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[HASH_ALGORITHM])

        # 역할 복호화
        if "role" in payload:
            payload["role"] = decrypt_role(payload["role"])

        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")
