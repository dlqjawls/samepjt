import pytest
from sqlmodel import Session, select, delete
from app.db.models.maintenance_history import MaintenanceHistory
from app.utils.lut_constants import ItemType
from faker import Faker
from datetime import datetime

fake = Faker()

from tests.helpers import master_token, semi_admin_token, create_dummy_vehicles, create_dummy_modules, create_dummy_options

@pytest.fixture
def clear_maintenance_histories(session: Session):
    """정비 기록 테이블 초기화"""
    session.execute(delete(MaintenanceHistory))
    session.commit()

def test_create_maintenance_history_success(client, session, master_token, clear_maintenance_histories, create_dummy_vehicles, create_dummy_modules, create_dummy_options):
    """✅ 정상적인 정비 기록 등록 테스트"""
    # Given: 정비 기록 등록 요청 데이터
    maintenance_history_data = {
        "item_type_name": "vehicle",
        "item_id": create_dummy_vehicles()[0].vehicle_id,
        "issue": "TEST_ISSUE",
        "cost": 10000,
        "scheduled_at": "2025-01-01T00:00:00Z",
        "completed_at": "2025-01-01T00:00:00Z"
    }

    # When: 마스터 권한으로 정비 기록 등록 요청
    response = client.post(
        "/api/admin/maintenance-history",
        json=maintenance_history_data,
        headers={"Authorization": f"Bearer {master_token}"}
    )

    # Then: 응답 검증
    assert response.status_code == 200
    data = response.json()
    assert data["resultCode"] == "SUCCESS"
    assert data["message"] == "Maintenance history created successfully"

    # Then: DB에 저장된 데이터 검증
    maintenance_history = session.exec(select(MaintenanceHistory).where(MaintenanceHistory.item_id == maintenance_history_data["item_id"])).first()
    assert maintenance_history is not None
    assert maintenance_history.item_type_id == ItemType.VEHICLE.ID
    assert maintenance_history.issue == maintenance_history_data["issue"]
    assert maintenance_history.cost == maintenance_history_data["cost"]
    assert maintenance_history.maintenance_status_id == 1
    assert maintenance_history.scheduled_at == datetime.strptime(maintenance_history_data["scheduled_at"], "%Y-%m-%dT%H:%M:%SZ")
    assert maintenance_history.completed_at == datetime.strptime(maintenance_history_data["completed_at"], "%Y-%m-%dT%H:%M:%SZ")


def test_create_maintenance_history_unauthorized(client, create_dummy_vehicles):
    """❌ 인증 없이 정비 기록 등록 시도"""
    maintenance_history_data = {
        "item_type": "vehicle",
        "item_id": create_dummy_vehicles()[0].vehicle_id,
        "issue": "TEST_ISSUE",
        "cost": 10000,
        "scheduled_at": "2025-01-01T00:00:00Z",
        "completed_at": "2025-01-01T00:00:00Z"
    } 
    response = client.post("/api/admin/maintenance-history", json=maintenance_history_data)
    assert response.status_code == 401

def test_create_maintenance_history_forbidden(client, semi_admin_token, create_dummy_vehicles):
    """❌ 권한 없는 사용자의 정비 기록 등록 시도"""
    maintenance_history_data = {
        "item_type_name": "vehicle",
        "item_id": create_dummy_vehicles()[0].vehicle_id,
        "issue": "TEST_ISSUE",
        "cost": 10000,
        "scheduled_at": "2025-01-01T00:00:00Z",
        "completed_at": "2025-01-01T00:00:00Z"
    }
    response = client.post(
        "/api/admin/maintenance-history",
        json=maintenance_history_data,
        headers={"Authorization": f"Bearer {semi_admin_token}"}
    )
    assert response.status_code == 403


@pytest.mark.parametrize("invalid_maintenance_history_data", [
    {},
    {"item_type": "vehicle", "item_id": "dummy"},
    {"item_type": "vehicle", "issue": "TEST_ISSUE"},
    {"item_type": "vehicle", "cost": 10000},
    {"item_type": "vehicle", "maintenance_status_id": 1},
    {"item_type": "vehicle", "scheduled_at": "2025-01-01T00:00:00Z"},
    {"item_type": "vehicle", "completed_at": "2025-01-01T00:00:00Z"},
])
def test_create_maintenance_history_missing_fields(client, master_token, invalid_maintenance_history_data, create_dummy_vehicles):
    """❌ 필수 필드 누락 테스트"""
    # if item_id가 필요하면, 대체할 실제 값을 설정
    if invalid_maintenance_history_data.get("item_id") == "dummy":
        invalid_maintenance_history_data["item_id"] = create_dummy_vehicles()[0].vehicle_id

    response = client.post(
        "/api/admin/maintenance-history",
        json=invalid_maintenance_history_data,
        headers={"Authorization": f"Bearer {master_token}"}
    )
    
    assert response.status_code == 422
    assert response.json()["resultCode"] == "FAILURE"
