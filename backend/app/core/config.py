import os
import logging
import base64
from dotenv import load_dotenv
from pydantic import BaseSettings, Field

# 환경 변수 로드
load_dotenv()

class Settings(BaseSettings):
    ENVIRONMENT: str = Field(default=os.getenv("ENVIRONMENT", "development"))
    DEBUG: bool = Field(default=os.getenv("DEBUG", "False").lower() == "true")
    HOST: str = Field(default=os.getenv("HOST", "0.0.0.0"))
    PORT: int = Field(default=int(os.getenv("PORT", 8000)))
    RELOAD: bool = Field(default=os.getenv("RELOAD", "False").lower() == "true")

    # SQLite 관련 설정
    DATABASE_URL: str = Field(default=os.getenv("DATABASE_URL", "sqlite:///./test.db"))

    # Redis 관련 설정
    UPSTASH_REDIS_REST_URL: str = Field(default=os.getenv("UPSTASH_REDIS_REST_URL", ""))
    UPSTASH_REDIS_REST_TOKEN: str = Field(default=os.getenv("UPSTASH_REDIS_REST_TOKEN", ""))

    # JWT 관련 설정
    SECRET_KEY: str = Field(default=os.getenv("JWT_SECRET_KEY", ""))
    ROLE_ENCRYPTION_KEY: str = Field(default=os.getenv("ROLE_ENCRYPTION_KEY", ""))

    HASH_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_SECONDS: int = Field(default=int(os.getenv("ACCESS_TOKEN_EXPIRE_SECONDS", 600)))
    REFRESH_TOKEN_EXPIRE_SECONDS: int = Field(default=int(os.getenv("REFRESH_TOKEN_EXPIRE_SECONDS", 1200)))

    @property
    def fernet_key(self) -> bytes:
        """ROLE_ENCRYPTION_KEY가 유효한지 검증 후 변환"""
        try:
            return base64.urlsafe_b64decode(self.ROLE_ENCRYPTION_KEY.encode())
        except Exception as e:
            raise ValueError(f"🚨 ROLE_ENCRYPTION_KEY가 올바른 Base64 형식이 아닙니다: {e}")

# 로깅 설정
logging.basicConfig(
    level=logging.DEBUG if os.getenv("DEBUG", "False").lower() == "true" else logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log", encoding="utf-8")  # 로그 파일 저장
    ]
)
logger = logging.getLogger(__name__)

settings = Settings()

logger.info(f"🔹 현재 환경: {settings.ENVIRONMENT}, Debug 모드: {settings.DEBUG}")
logger.info(f"🔹 서버 실행: {settings.HOST}:{settings.PORT}, Reload: {settings.RELOAD}")
logger.info("✅ 환경 변수 및 로깅 설정 완료.")
