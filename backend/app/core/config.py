import os
import logging
import base64
from dotenv import load_dotenv
from pydantic import BaseSettings, Field, validator
from typing import Optional
from app.utils.exceptions import ConfigError
from cryptography.fernet import Fernet

# 환경 변수 로드
load_dotenv()

class Settings(BaseSettings):
    # 기본 설정
    ENVIRONMENT: str = Field(default=os.getenv("ENVIRONMENT", "development"))
    DEBUG: bool = Field(default=os.getenv("DEBUG", "False").lower() == "true")
    HOST: str = Field(default=os.getenv("HOST", "0.0.0.0"))
    PORT: int = Field(default=int(os.getenv("PORT", 8000)))
    RELOAD: bool = Field(default=os.getenv("RELOAD", "False").lower() == "true")

    # 데이터베이스 설정
    DATABASE_URL: str = Field(default=os.getenv("DATABASE_URL", "sqlite:///database.db"))

    # Redis 설정
    UPSTASH_REDIS_REST_URL: str
    UPSTASH_REDIS_REST_TOKEN: str

    # JWT 설정
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_SECONDS: int = Field(default=int(os.getenv("ACCESS_TOKEN_EXPIRE_SECONDS", 600)))
    REFRESH_TOKEN_EXPIRE_SECONDS: int = Field(default=int(os.getenv("REFRESH_TOKEN_EXPIRE_SECONDS", 1200)))

    ROLE_ENCRYPTION_KEY: str
    
    aws_access_key_id: str = Field(..., env="AWS_S3_ACCESS_KEY_ID")
    aws_secret_access_key: str = Field(..., env="AWS_S3_SECRET_ACCESS_KEY")
    aws_region: str = Field(..., env="AWS_S3_REGION")
    s3_bucket_name: str = Field(..., env="AWS_S3_BUCKET")

    @validator("UPSTASH_REDIS_REST_URL", "UPSTASH_REDIS_REST_TOKEN", "JWT_SECRET_KEY")
    def validate_required_env(cls, v: str, field: str) -> str:
        """필수 환경 변수 검증"""
        if not v:
            raise ConfigError(
                message=f"Missing required environment variable",
                detail={
                    "field": field,
                    "current_value": v
                }
            )
        return v

    @validator("ACCESS_TOKEN_EXPIRE_SECONDS", "REFRESH_TOKEN_EXPIRE_SECONDS")
    def validate_positive_number(cls, v: int, field: str) -> int:
        """양수 값 검증"""
        if v <= 0:
            raise ConfigError(
                message=f"Invalid value for {field}: must be positive",
                detail={
                    "field": field,
                    "value": v,
                    "constraint": "must be positive"
                }
            )
        return v

    @validator("DATABASE_URL")
    def validate_database_url(cls, v: str) -> str:
        """데이터베이스 URL 검증"""
        if not v.startswith(("sqlite:///", "postgresql://", "mysql://")):
            raise ConfigError(
                message="Invalid database URL format",
                detail={
                    "current_url": v,
                    "supported_formats": ["sqlite:///", "postgresql://", "mysql://"]
                }
            )
        return v

    @validator("ROLE_ENCRYPTION_KEY")
    def validate_encryption_key(cls, v: str) -> str:
        """ROLE_ENCRYPTION_KEY 검증"""
        try:
            decoded_key = base64.urlsafe_b64decode(v.encode())
            if len(decoded_key) != 32:
                raise ConfigError(
                    message="Invalid ROLE_ENCRYPTION_KEY format",
                    detail={
                        "error": "ROLE_ENCRYPTION_KEY must be 32-byte Base64 URL-Safe string",
                        "key_length": len(decoded_key)
                    }
                )
            # Fernet 키 생성 테스트
            Fernet(v.encode())
            return v
        except Exception as e:
            raise e

    @property
    def fernet_instance(self) -> Fernet:
        """검증된 Fernet 인스턴스 반환"""
        return Fernet(self.ROLE_ENCRYPTION_KEY.encode())

    class Config:
        env_file = ".env"
        case_sensitive = True

try:
    # 설정 객체 생성
    settings = Settings(
        UPSTASH_REDIS_REST_URL=os.getenv("UPSTASH_REDIS_REST_URL", ""),
        UPSTASH_REDIS_REST_TOKEN=os.getenv("UPSTASH_REDIS_REST_TOKEN", ""),
        JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY", ""),
        ROLE_ENCRYPTION_KEY=os.getenv("ROLE_ENCRYPTION_KEY", ""),
        aws_access_key_id=os.getenv("AWS_S3_ACCESS_KEY_ID", ""),
        aws_secret_access_key=os.getenv("AWS_S3_SECRET_ACCESS_KEY", ""),
        aws_region=os.getenv("AWS_S3_REGION", ""),
        s3_bucket_name=os.getenv("AWS_S3_BUCKET", "")
    )

    # 로깅 설정
    logging.basicConfig(
        level=logging.DEBUG if settings.DEBUG else logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("app.log", encoding="utf-8")
        ]
    )
    logger = logging.getLogger(__name__)

    # 초기화 로깅
    logger.info(f"🔹 현재 환경: {settings.ENVIRONMENT}, Debug 모드: {settings.DEBUG}")
    logger.info(f"🔹 서버 실행: {settings.HOST}:{settings.PORT}, Reload: {settings.RELOAD}")
    logger.info("✅ 환경 변수 및 로깅 설정 완료.")

except Exception as e:
    raise e