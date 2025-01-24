import os
from sqlmodel import SQLModel, Session, create_engine
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

engine = create_engine(settings.DATABASE_URL, echo=settings.DEBUG)

def get_session():
    with Session(engine) as session:
        yield session

async def initialize_database():
    try:
        logger.info("🔹 데이터베이스 초기화 중...")
        SQLModel.metadata.create_all(engine)
        logger.info("✅ 데이터베이스 초기화 완료.")
    except Exception as e:
        logger.error(f"🚨 데이터베이스 초기화 실패: {e}")
