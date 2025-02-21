import pytest
from datetime import datetime
from app.db.models.maintenance_history import MaintenanceHistory
from sqlmodel import Session, select
from app.utils.lut_constants import ItemStatus
import json

from tests.helpers import master_token, semi_admin_token

@pytest.fixture
def test_maintenance_history(session: Session):
    """테스트용 정비 기록 데이터 생성"""
    maintenance_history = MaintenanceHistory(
        maintenance_id=11,
        item_type_id=1,
        item_id=1,
        issue="Test Issue",
        cost=100000,
        maintenance_status_id=1,
        scheduled_at=datetime.now(),
        completed_at=datetime.now(),
        created_by=1,
        updated_by=1,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    session.add(maintenance_history)
    session.commit()
    session.refresh(maintenance_history)
    return maintenance_history

def get_maintenance_history_id(session: Session, maintenance_history_id: int) -> int:
    """정비 기록 ID 조회"""
    maintenance_history = session.exec(select(MaintenanceHistory).where(MaintenanceHistory.maintenance_id == maintenance_history_id)).first()
    if not maintenance_history or not maintenance_history.maintenance_id:
        raise ValueError(f"Maintenance history with id {maintenance_history_id} not found")
    return maintenance_history.maintenance_id

def test_update_maintenance_history_success(client, session, master_token, test_maintenance_history):
    """✅ 정상적인 정비 기록 정보 업데이트 테스트"""
    # Given: 업데이트할 정비 기록 데이터
    update_data = {
        "issue": "Updated Issue",
        "cost": 200000,
        "maintenance_status_id": 2,
    }

    # When: 마스터 권한으로 정비 기록 정보 업데이트 요청
    response = client.patch(
        f"/api/admin/maintenance-history/{get_maintenance_history_id(session, test_maintenance_history.maintenance_id)}",
        json=update_data,
        headers={"Authorization": f"Bearer {master_token}"}
    )

    # Then: 응답 검증
    assert response.status_code == 200
    data = response.json()
    assert data["resultCode"] == "SUCCESS"
    assert data["message"] == "Maintenance history updated successfully"

    # Then: DB에 저장된 데이터 검증
    updated_maintenance_history = session.exec(
        select(MaintenanceHistory).where(MaintenanceHistory.maintenance_id == get_maintenance_history_id(session, test_maintenance_history.maintenance_id))
    ).first()
    assert updated_maintenance_history.maintenance_id is not None
    assert updated_maintenance_history.issue is not None
    assert updated_maintenance_history.cost is not None
    assert updated_maintenance_history.maintenance_status_id is not None

def test_update_maintenance_history_unauthorized(client, session, test_maintenance_history, semi_admin_token):
    """❌ 권한 없는 사용자의 정비 기록 정보 업데이트 시도"""
    update_data = {
        "issue": "Updated Issue",
        "cost": 200000,
        "maintenance_status_id": 2,
    }

    response = client.patch(
        f"/api/admin/maintenance-history/{get_maintenance_history_id(session, test_maintenance_history.maintenance_id)}",
        json=update_data,
        headers={"Authorization": f"Bearer {semi_admin_token}"}
    )

    assert response.status_code == 403
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "Permission denied" in data["message"]

def test_update_nonexistent_maintenance_history(client, session, master_token):
    """❌ 존재하지 않는 정비 기록 정보 업데이트 시도"""
    update_data = {
        "issue": "Updated Issue",
        "cost": 200000,
        "maintenance_status_id": 2,
    }

    response = client.patch(
        "/api/admin/maintenance-history/99999",
        json=update_data,
        headers={"Authorization": f"Bearer {master_token}"}
    )

    assert response.status_code == 404
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "Maintenance history not found" in data["message"]


def test_update_maintenance_history_without_token(client, session, test_maintenance_history):
    """❌ 인증 토큰 없이 정비 기록 정보 업데이트 시도"""
    update_data = {
        "issue": "Updated Issue",
        "cost": 200000,
        "maintenance_status_id": 2,
    }

    response = client.patch(
        f"/api/admin/maintenance-history/{get_maintenance_history_id(session, test_maintenance_history.maintenance_id)}",
        json=update_data
    )

    assert response.status_code == 401
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "Authentication" in data["message"]

