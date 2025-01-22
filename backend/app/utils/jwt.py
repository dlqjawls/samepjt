import app.schemas.jwt as jwt
import datetime
from typing import Optional

# 환경 변수에서 SECRET_KEY 로드 (하드코딩 금지)
import os
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "default_secret_key")  # 환경 변수로 설정해야 함
HASH_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = 43200  # 12시간
REFRESH_TOKEN_EXPIRE_DAYS = 7  # 리프레시 토큰 만료 시간 (7일)

def create_access_token(userPK: int, role: str = "user", expires_delta: Optional[int] = None) -> str:
    """
    JWT 액세스 토큰 생성
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    expires = now + datetime.timedelta(seconds=expires_delta or ACCESS_TOKEN_EXPIRE_SECONDS)

    payload = {
        "userPK": userPK,
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
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")
