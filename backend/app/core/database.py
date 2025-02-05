from sqlmodel import create_engine, SQLModel, Session, select
from app.core.config import settings
from app.utils.exceptions import DatabaseError
import logging
from typing import Any, Dict, Generator
from datetime import datetime
import time

from app.models import (
    Role, ItemStatus, ItemType, ModuleType, MaintenanceStatus,
    UsageStatus, RentStatus, VideoType, PaymentStatus, PaymentMethod
)
from app.utils.lut_constants import (
    ROLE_MAPPING, ITEM_STATUS_MAPPING, ITEM_TYPE_MAPPING, MODULE_TYPE_MAPPING,
    MAINTENANCE_STATUS_MAPPING, USAGE_STATUS_MAPPING, RENT_STATUS_MAPPING,
    VIDEO_TYPE_MAPPING, PAYMENT_STATUS_MAPPING, PAYMENT_METHOD_MAPPING
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
                
        validate_lut_mappings(session)
                
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

def validate_lut_mappings(session: Session) -> None:
    """
    DB의 LUT 값과 상수값이 일치하는지 검증.
    일치하지 않으면 예외를 발생시킵니다.
    """
    errors = []

    # 역할 (Role)
    roles = session.exec(select(Role)).all()
    db_role_mapping = {role.role_id: role.role_name for role in roles}
    if db_role_mapping != ROLE_MAPPING:
        errors.append(f"Role mismatch: DB: {db_role_mapping} vs Constant: {ROLE_MAPPING}")

    # 아이템 상태 (Item Status)
    item_statuses = session.exec(select(ItemStatus)).all()
    db_item_status_mapping = {status.item_status_id: status.item_status_name for status in item_statuses}
    if db_item_status_mapping != ITEM_STATUS_MAPPING:
        errors.append(f"ItemStatus mismatch: DB: {db_item_status_mapping} vs Constant: {ITEM_STATUS_MAPPING}")

    # 아이템 유형 (Item Type)
    item_types = session.exec(select(ItemType)).all()
    db_item_type_mapping = {item.item_type_id: item.item_type_name for item in item_types}
    if db_item_type_mapping != ITEM_TYPE_MAPPING:
        errors.append(f"ItemType mismatch: DB: {db_item_type_mapping} vs Constant: {ITEM_TYPE_MAPPING}")

    # 모듈 유형 (Module Type)
    module_types = session.exec(select(ModuleType)).all()
    db_module_type_mapping = {
        mt.module_type_id: {"name": mt.module_type_name, "size": mt.module_type_size, "cost": mt.module_type_cost}
        for mt in module_types
    }
    if db_module_type_mapping != MODULE_TYPE_MAPPING:
        errors.append(f"ModuleType mismatch: DB: {db_module_type_mapping} vs Constant: {MODULE_TYPE_MAPPING}")

    # 유지보수 상태 (Maintenance Status)
    maintenance_statuses = session.exec(select(MaintenanceStatus)).all()
    db_maintenance_status_mapping = {ms.maintenance_status_id: ms.maintenance_status_name for ms in maintenance_statuses}
    if db_maintenance_status_mapping != MAINTENANCE_STATUS_MAPPING:
        errors.append(f"MaintenanceStatus mismatch: DB: {db_maintenance_status_mapping} vs Constant: {MAINTENANCE_STATUS_MAPPING}")

    # 사용 기록 상태 (Usage Status)
    usage_statuses = session.exec(select(UsageStatus)).all()
    db_usage_status_mapping = {us.usage_status_id: us.usage_status_name for us in usage_statuses}
    if db_usage_status_mapping != USAGE_STATUS_MAPPING:
        errors.append(f"UsageStatus mismatch: DB: {db_usage_status_mapping} vs Constant: {USAGE_STATUS_MAPPING}")

    # 대여 상태 (Rent Status)
    rent_statuses = session.exec(select(RentStatus)).all()
    db_rent_status_mapping = {rs.rent_status_id: rs.rent_status_name for rs in rent_statuses}
    if db_rent_status_mapping != RENT_STATUS_MAPPING:
        errors.append(f"RentStatus mismatch: DB: {db_rent_status_mapping} vs Constant: {RENT_STATUS_MAPPING}")

    # 비디오 유형 (Video Type)
    video_types = session.exec(select(VideoType)).all()
    db_video_type_mapping = {vt.video_type_id: vt.video_type_name for vt in video_types}
    if db_video_type_mapping != VIDEO_TYPE_MAPPING:
        errors.append(f"VideoType mismatch: DB: {db_video_type_mapping} vs Constant: {VIDEO_TYPE_MAPPING}")

    # 결제 상태 (Payment Status)
    payment_statuses = session.exec(select(PaymentStatus)).all()
    db_payment_status_mapping = {ps.payment_status_id: ps.payment_status_name for ps in payment_statuses}
    if db_payment_status_mapping != PAYMENT_STATUS_MAPPING:
        errors.append(f"PaymentStatus mismatch: DB: {db_payment_status_mapping} vs Constant: {PAYMENT_STATUS_MAPPING}")

    # 결제 방식 (Payment Method)
    payment_methods = session.exec(select(PaymentMethod)).all()
    db_payment_method_mapping = {pm.payment_method_id: pm.payment_method_name for pm in payment_methods}
    if db_payment_method_mapping != PAYMENT_METHOD_MAPPING:
        errors.append(f"PaymentMethod mismatch: DB: {db_payment_method_mapping} vs Constant: {PAYMENT_METHOD_MAPPING}")

    if errors:
        for err in errors:
            logger.error(err)
        raise Exception("LUT 검증 실패: DB와 상수 LUT 값이 일치하지 않습니다!")
    else:
        logger.info("LUT 검증 성공: DB와 상수 LUT 값이 일치합니다.")