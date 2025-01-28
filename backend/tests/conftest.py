import pytest
from fastapi.testclient import TestClient
from sqlmodel import create_engine, SQLModel, Session
import logging

from app.main import create_app
from app.core.database import get_session
from app import seed
from app.models.user import User  # User 모델 import

# 로깅 설정
logger = logging.getLogger(__name__)


# 테스트용 DB 설정
TEST_DATABASE_URL = "sqlite:///./tests/test.db"
test_engine = create_engine(TEST_DATABASE_URL, echo=False)

@pytest.fixture(scope="session", autouse=True)
def create_test_db():
    """전체 테스트 세션에서 한 번만 실행: DB 스키마 생성"""
    SQLModel.metadata.create_all(test_engine)
    yield
    test_engine.dispose()

@pytest.fixture(autouse=True)
def reset_test_db():
    """각 테스트 함수 실행 전에 데이터베이스 초기화"""
    # 1. 모든 테이블의 데이터 삭제
    with Session(test_engine) as session:
        # User 테이블 초기화 (foreign key 제약조건 때문에 순서 중요)
        session.query(User).delete()
        session.commit()
        
        try:
            # 2. seed 데이터 재삽입
            seed.seed_data(session)
            session.commit()
            logger.info("✅ Test database reset successful")
        except Exception as e:
            logger.error(f"❌ Error resetting test database: {e}")
            session.rollback()
            raise

@pytest.fixture
def session():
    """각 테스트마다 독립적인 세션 제공"""
    with Session(test_engine) as sess:
        yield sess

@pytest.fixture
def client(session):
    """FastAPI TestClient 제공"""
    app = create_app()
    
    def _override_get_session():
        yield session

    app.dependency_overrides[get_session] = _override_get_session
    
    with TestClient(app) as c:
        yield c