from cryptography.fernet import Fernet
import jwt
import datetime
from typing import Optional
import os
from app.core.redis_config import redis_config

# 환경 변수에서 SECRET_KEY 및 ROLE_ENCRYPTION_KEY 로드
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "default_secret_key")  # JWT 서명용 비밀키
ROLE_ENCRYPTION_KEY = os.getenv("ROLE_ENCRYPTION_KEY", Fernet.generate_key().decode())  # 역할 암호화 키

HASH_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = 600   # 10분 (600초)
REFRESH_TOKEN_EXPIRE_SECONDS = 1200 # 20분 (1200초)

# 대칭키 암호화 도구 초기화
fernet = Fernet(ROLE_ENCRYPTION_KEY.encode())

# Redis 연결
redis_client = redis_config()

def encrypt_role(role: str) -> str:
    return fernet.encrypt(role.encode()).decode()

def decrypt_role(encrypted_role: str) -> str:
    return fernet.decrypt(encrypted_role.encode()).decode()

def create_access_token(userPK: int, role: str = "user", expires_delta: Optional[int] = None) -> str:
    now = datetime.datetime.now(datetime.timezone.utc)
    expires = now + datetime.timedelta(seconds=expires_delta or ACCESS_TOKEN_EXPIRE_SECONDS)

    encrypted_role = encrypt_role(role)

    payload = {
        "userPK": userPK,
        "role": encrypted_role,
        "iat": now,
        "exp": expires,
        "type": "access"
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=HASH_ALGORITHM)

def create_refresh_token(userPK: int) -> str:
    now = datetime.datetime.now(datetime.timezone.utc)
    expires = now + datetime.timedelta(seconds=REFRESH_TOKEN_EXPIRE_SECONDS)

    payload = {
        "userPK": userPK,
        "iat": now,
        "exp": expires,
        "type": "refresh"
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=HASH_ALGORITHM)

def save_refresh_token(userPK: int, role: str, refresh_token: str):
    redis_key = f"user:{role}:{userPK}:refresh_token"
    redis_client.setex(redis_key, refresh_token, REFRESH_TOKEN_EXPIRE_SECONDS)  

def get_refresh_token(userPK: int, role: str) -> Optional[str]:
    redis_key = f"user:{role}:{userPK}:refresh_token"
    return redis_client.get(redis_key)

def is_valid_refresh_token(userPK: int, role: str, refresh_token: str) -> bool:
    stored_token = get_refresh_token(userPK, role)
    return stored_token is not None and stored_token == refresh_token

def refresh_access_token(userPK: int, role: str, refresh_token: str) -> Optional[str]:
    if is_valid_refresh_token(userPK, role, refresh_token):
        return create_access_token(userPK, role)
    return None

def delete_refresh_token(userPK: int, role: str):
    redis_key = f"user:{role}:{userPK}:refresh_token"
    redis_client.delete(redis_key)

def create_token(userPK: int, role: str = "user") -> tuple:
    access_token = create_access_token(userPK, role)
    refresh_token = create_refresh_token(userPK)
    save_refresh_token(userPK, role, refresh_token)
    return access_token, refresh_token

def decode_jwt_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[HASH_ALGORITHM])

        if "role" in payload:
            payload["role"] = decrypt_role(payload["role"])

        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")
