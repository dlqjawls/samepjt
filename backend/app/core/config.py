import os
import logging
from dotenv import load_dotenv
from pydantic import BaseSettings

# 환경 변수 로드
load_dotenv()

class Settings(BaseSettings):
    """환경 변수 설정 클래스"""
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    RELOAD: bool = os.getenv("RELOAD", "False").lower() == "true"

    # Redis 관련 설정
    UPSTASH_REDIS_REST_URL: str = os.getenv("UPSTASH_REDIS_REST_URL", "")
    UPSTASH_REDIS_REST_TOKEN: str = os.getenv("UPSTASH_REDIS_REST_TOKEN", "")

    # JWT 관련 설정
    SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "default_secret_key")
    ROLE_ENCRYPTION_KEY: str = os.getenv("ROLE_ENCRYPTION_KEY", "")
    HASH_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_SECONDS: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_SECONDS", 600))   # ✅ 정수 변환
    REFRESH_TOKEN_EXPIRE_SECONDS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_SECONDS", 1200)) # ✅ 정수 변환

# 로깅 설정
logging.basicConfig(
    level=logging.DEBUG if os.getenv("DEBUG", "False").lower() == "true" else logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 설정 인스턴스
settings = Settings()

logger.info(f"🔹 현재 환경: {settings.ENVIRONMENT}, Debug 모드: {settings.DEBUG}")
logger.info(f"🔹 서버 실행: {settings.HOST}:{settings.PORT}, Reload: {settings.RELOAD}")
logger.info("✅ 환경 변수 및 로깅 설정 완료.")
