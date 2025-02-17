from sqlmodel import create_engine, SQLModel, Session, select
from app.core.config import settings
from app.utils.exceptions import DatabaseError
import logging
from typing import Any, Dict, Generator
from datetime import datetime
import time

from app.db.models import (
    Role, ItemStatus, ItemType, ModuleType, MaintenanceStatus,
    UsageStatus, RentStatus, VideoType, PaymentStatus, PaymentMethod
)

logger = logging.getLogger(__name__)

def create_db_engine():
    """데이터베이스 엔진 생성"""
    try:
        engine = create_engine(
            settings.DATABASE_URL,
            # echo=settings.DEBUG,
            connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
        )
        logger.info("✅ 데이터베이스 엔진 생성 완료")
        return engine
    except Exception as e:
        raise DatabaseError(
            message="Failed to create database engine",
            detail={
                "error": str(e),
                "database_url": settings.DATABASE_URL
            }
        )

engine = create_db_engine()

def get_session() -> Generator[Session, None, None]:
    """데이터베이스 세션 제공"""
    session = Session(engine)
    try:
        yield session
        
    finally:
        session.close()

async def initialize_database() -> None:
    """데이터베이스 초기화 및 시드 데이터 삽입"""
    try:
        logger.info("🔹 데이터베이스 스키마 생성 중...")
        SQLModel.metadata.create_all(engine)
        logger.info("✅ 데이터베이스 스키마 생성 완료")
            
        logger.info("🔹 초기 데이터 삽입 중...")
        with Session(engine) as session:
            try:
                from app import seed
                seed.seed_data(session)
                session.commit()
                logger.info("✅ 초기 데이터 삽입 완료")
            except Exception as e:
                session.rollback()
                raise DatabaseError(
                    message="Failed to insert seed data",
                    detail={"error": str(e)}
                )
                
    except Exception as e:
        if isinstance(e, DatabaseError):
            raise e
        raise DatabaseError(
            message="Database initialization failed",
            detail={
                "error": str(e),
                "database_url": settings.DATABASE_URL
            }
        )

def verify_database_connection(max_retries: int = 3, retry_delay: int = 1) -> Dict[str, Any]:
    start_time = datetime.now()
    
    for attempt in range(max_retries):
        try:
            with Session(engine) as session:
                query_start = time.time()
                session.exec(select(1)).first()
                response_time = (time.time() - query_start) * 1000

                return {
                    "status": True,
                    "message": "데이터베이스 연결 성공",
                    "response_time_ms": round(response_time, 2),
                    "checked_at": datetime.now().isoformat(),
                    "engine_info": {
                        "url": str(engine.url),
                        "pool_size": engine.pool.size(),
                        "pool_overflow": engine.pool.overflow()
                    },
                    "attempts": attempt + 1
                }

        except Exception as e:
            logger.error(f"🚨 데이터베이스 연결 실패 (시도 {attempt + 1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
    
    # 모든 시도 실패 시 반환되는 기본값
    return {
        "status": False,
        "message": "모든 연결 시도 실패",
        "checked_at": datetime.now().isoformat(),
        "attempts": max_retries,
        "total_time_ms": round((datetime.now() - start_time).total_seconds() * 1000, 2)
    }