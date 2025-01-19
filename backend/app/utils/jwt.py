import jwt
import datetime
from typing import Optional

# 디버그용으로 사용할 SECRET_KEY 
SECRET_KEY = "debug-secret-key" #TODO: Change environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = 86400  # 24시간


def create_jwt_token(user_id: str, role: str = "user", expires_delta: Optional[int] = None) -> str:
    """
    JWT 토큰을 생성하는 함수

    Args:
        user_id (str): 사용자 ID
        role (str): 사용자 역할 (default: "user")
        expires_delta (int, optional): 토큰 만료 시간 (초 단위) (기본값: 24시간)

    Returns:
        str: 생성된 JWT 토큰
    """
    now = datetime.datetime.utcnow()
    expires = now + datetime.timedelta(seconds=expires_delta or ACCESS_TOKEN_EXPIRE_SECONDS)  # 만료 시간 설정

    payload = {
        "sub": user_id,  # subject (사용자 ID)
        "role": role,  # 사용자 역할
        "exp": expires,  # 만료 시간
        "iat": now,  # 발급 시간
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def decode_jwt_token(token: str) -> dict:
    """
    JWT 토큰을 검증하고 payload를 반환하는 함수

    Args:
        token (str): 검증할 JWT 토큰

    Returns:
        dict: payload 데이터

    Raises:
        jwt.ExpiredSignatureError: 토큰이 만료된 경우
        jwt.InvalidTokenError: 토큰이 잘못된 경우
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")