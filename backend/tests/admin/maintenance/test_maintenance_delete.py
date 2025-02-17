import pytest
from sqlmodel import Session, select
from app.db.models.maintenance_history import MaintenanceHistory
from datetime import datetime

from tests.helpers import master_token, semi_admin_token


@pytest.fixture
def test_maintenance_history(session: Session):
    """테스트용 정비 기록 데이터 생성"""
    history = MaintenanceHistory(
        maintenance_id=1,
        item_id=1,
        item_type_id=1,
        issue="Test Issue",
        cost=10000,
        maintenance_status_id=1,
        scheduled_at=datetime.now(),
        completed_at=datetime.now(),
        created_by=1,
        updated_by=1,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    session.add(history)
    session.commit()
    session.refresh(history)
    return history

def get_maintenance_history_id(session: Session, maintenance_id: int) -> int:
    """정비 기록 ID 조회"""
    history = session.exec(select(MaintenanceHistory).where(MaintenanceHistory.maintenance_id == maintenance_id)).first()
    if not history or not history.maintenance_id:
        raise ValueError(f"Maintenance history with id {maintenance_id} not found")
    return history.maintenance_id
  

def test_delete_maintenance_history_success(client, session, master_token, test_maintenance_history):
    """✅ 정비 기록 삭제 성공 테스트"""
    response = client.delete( 
        f"/admin/maintenance-history/{get_maintenance_history_id(session, test_maintenance_history.maintenance_id)}",
        headers={"Authorization": f"Bearer {master_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["resultCode"] == "SUCCESS"
    assert data["message"] == "Maintenance history deleted successfully"

def test_delete_maintenance_history_not_found(client, master_token):
    """❌ 존재하지 않는 정비 기록 삭제 시도 테스트"""
    response = client.delete(
        "/admin/maintenance-history/9999",  # 존재하지 않는 ID
        headers={"Authorization": f"Bearer {master_token}"}
    )

    assert response.status_code == 404
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert data["error_code"] == "NOT_FOUND"

# 추가: 인증 토큰 없이 정비 기록 삭제 시도 테스트
def test_delete_maintenance_history_without_token(client, session, test_maintenance_history):
    """❌ 인증 토큰 없이 정비 기록 삭제 시도 테스트"""
    response = client.delete(f"/admin/maintenance-history/{get_maintenance_history_id(session, test_maintenance_history.maintenance_id)}")
    assert response.status_code == 401
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    # 에러 메시지에 인증 관련 내용이 포함된 것을 확인
    assert "authentication" in data["message"].lower()

# 추가: 일반 관리자(권한 부족) 토큰으로 정비 기록 삭제 시도 테스트
def test_delete_maintenance_history_with_non_master_token(client, session, test_maintenance_history, semi_admin_token):
    """❌ 일반 관리자(권한 부족) 토큰으로 정비 기록 삭제 시도 테스트"""
    response = client.delete(
        f"/admin/maintenance-history/{get_maintenance_history_id(session, test_maintenance_history.maintenance_id)}",
        headers={"Authorization": f"Bearer {semi_admin_token}"}
    )
    assert response.status_code == 403
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    # 에러 메시지에 권한 거부 관련 내용이 포함된 것을 확인
    assert "permission denied" in data["message"].lower()

# 추가: 잘못된 형식의 정비 기록 ID로 삭제 시도 테스트
@pytest.mark.parametrize("invalid_maintenance_history_id", ["abc", -1, 0])
def test_delete_maintenance_history_invalid_id(client, master_token, invalid_maintenance_history_id):
    """🚨 잘못된 형식의 정비 기록 ID로 삭제 시도 테스트"""
    response = client.delete(
        f"/admin/maintenance-history/{invalid_maintenance_history_id}",
        headers={"Authorization": f"Bearer {master_token}"}
    )
    assert response.status_code == 422    
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    # 메시지에 검증 오류 상세 내용(예: "value is not a valid integer") 또는 "validation" 키워드가 포함되는지 확인
    assert "value is not a valid integer" in str(data["detail"]).lower() or "validation" in data["message"].lower()

# 추가: 이미 삭제된 정비 기록 재삭제 시도 테스트
def test_delete_maintenance_history_already_deleted(client, session, master_token, test_maintenance_history):
    """✅ 이미 삭제된 정비 기록 재삭제 시도 테스트"""
    # 첫 번째 삭제 시도 -> 성공 (soft delete)
    response_first = client.delete(
        f"/admin/maintenance-history/{get_maintenance_history_id(session, test_maintenance_history.maintenance_id)}",
        headers={"Authorization": f"Bearer {master_token}"}
    )
    assert response_first.status_code == 200
    data_first = response_first.json()
    assert data_first["resultCode"] == "SUCCESS"
    
    # 두 번째 삭제 시도 -> 이미 삭제되어 존재하지 않으므로 404 Not Found
    response_second = client.delete(
        f"/admin/maintenance-history/{get_maintenance_history_id(session, test_maintenance_history.maintenance_id)}",
        headers={"Authorization": f"Bearer {master_token}"}
    )
    assert response_second.status_code == 404
    data_second = response_second.json()
    assert data_second["resultCode"] == "FAILURE"
    assert data_second["error_code"] == "NOT_FOUND"
