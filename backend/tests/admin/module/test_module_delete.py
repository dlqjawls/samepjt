import pytest
from sqlmodel import Session
from app.db.models.usage_history import UsageHistory
from app.db.models.module import Module
from app.core.jwt import jwt_handler
from app.utils.lut_constants import ItemStatus, ItemType, RentStatus, UsageStatus
from datetime import datetime
from app.db.models.rent_history import RentHistory

@pytest.fixture
def master_token():
    """마스터 권한 토큰 생성"""
    return jwt_handler.create_token(1, role="master")[0]

# 추가: 일반 관리자(권한 부족) 토큰 생성 피스쳐
@pytest.fixture
def semi_admin_token():
    """일반 관리자(권한 부족) 토큰 생성"""
    return jwt_handler.create_token(2, role="semi")[0]

@pytest.fixture
def test_module(session: Session):
    """테스트용 모듈 데이터 생성"""
    module = Module(
        module_nfc_tag_id="1A1FF1043E2BC6",
        module_type_id=1,
        current_location='{"x": 12.313, "y": 32.3232}',
        status_id=ItemStatus.INACTIVE,
        created_by=1,
        updated_by=1,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    session.add(module)
    session.commit()
    session.refresh(module)
    return module

@pytest.fixture
def rented_module(session: Session):
    """대여 중인 모듈 데이터 생성"""
    module = Module(
        module_nfc_tag_id="1A1FF1043E2BC6",
        module_type_id=1,
        current_location='{"x": 12.313, "y": 32.3232}',
        status_id=ItemStatus.ACTIVE,
        created_by=1,
        updated_by=1,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    session.add(module)
    session.commit()
    session.refresh(module)

    # 대여 이력 추가
    rent_history = RentHistory(
        user_pk=1,
        departure_location='{"x": 12.313, "y": 32.3232}',
        arrival_location='{"x": 12.313, "y": 32.3232}',
        cost=100000,
        mileage=10000,
        status_id=RentStatus.IN_PROGRESS,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    session.add(rent_history)
    session.commit()

    # 사용 기록 추가: delete_module에서 모듈 사용 여부를 확인할 때 사용
    usage_history = UsageHistory(
         rent_id=rent_history.rent_id,
         item_id=module.module_id,
         item_type_id=ItemType.MODULE,
         status_id=UsageStatus.IN_USE,
         created_at=datetime.now(),
         updated_at=datetime.now()
    )
    session.add(usage_history)
    session.commit()
    
    return module
  

def test_delete_module_success(client, session, master_token, test_module):
    """✅ 모듈 삭제 성공 테스트"""
    response = client.delete(
        f"/admin/modules/{test_module.module_id}",
        headers={"Authorization": f"Bearer {master_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["resultCode"] == "SUCCESS"
    assert data["message"] == "Module deleted successfully"

def test_delete_module_not_found(client, master_token):
    """❌ 존재하지 않는 모듈 삭제 시도 테스트"""
    response = client.delete(
        "/admin/modules/9999",  # 존재하지 않는 ID
        headers={"Authorization": f"Bearer {master_token}"}
    )

    assert response.status_code == 404
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert data["message"] == "Module not found"
    assert data["error_code"] == "NOT_FOUND"

def test_delete_module_in_use(client, session, master_token, rented_module):
    """❌ 대여 중인 모듈 삭제 시도 테스트"""
    response = client.delete(
        f"/admin/modules/{rented_module.module_id}",
        headers={"Authorization": f"Bearer {master_token}"}
    )

    assert response.status_code == 409
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert data["message"] == "Module is currently in use and cannot be deleted"
    assert data["error_code"] == "CONFLICT"

# 추가: 인증 토큰 없이 모듈 삭제 시도 테스트
def test_delete_module_without_token(client, session, test_module):
    """❌ 인증 토큰 없이 모듈 삭제 시도 테스트"""
    response = client.delete(f"/admin/modules/{test_module.module_id}")
    assert response.status_code == 401
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    # 에러 메시지에 인증 관련 내용이 포함된 것을 확인
    assert "authentication" in data["message"].lower()

# 추가: 일반 관리자(권한 부족) 토큰으로 모듈 삭제 시도 테스트
def test_delete_module_with_non_master_token(client, session, test_module, semi_admin_token):
    """❌ 일반 관리자(권한 부족) 토큰으로 모듈 삭제 시도 테스트"""
    response = client.delete(
        f"/admin/modules/{test_module.module_id}",
        headers={"Authorization": f"Bearer {semi_admin_token}"}
    )
    assert response.status_code == 403
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    # 에러 메시지에 권한 거부 관련 내용이 포함된 것을 확인
    assert "permission denied" in data["message"].lower()

# 추가: 잘못된 형식의 모듈 ID로 삭제 시도 테스트
@pytest.mark.parametrize("invalid_module_id", ["abc", -1, 0])
def test_delete_module_invalid_id(client, master_token, invalid_module_id):
    """🚨 잘못된 형식의 모듈 ID로 삭제 시도 테스트"""
    response = client.delete(
        f"/admin/modules/{invalid_module_id}",
        headers={"Authorization": f"Bearer {master_token}"}
    )
    assert response.status_code == 422
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    # 메시지에 검증 오류 상세 내용(예: "value is not a valid integer") 또는 "validation" 키워드가 포함되는지 확인
    assert "value is not a valid integer" in str(data["detail"]).lower() or "validation" in data["message"].lower()

# 추가: 이미 삭제된 모듈 재삭제 시도 테스트
def test_delete_module_already_deleted(client, session, master_token, test_module):
    """✅ 이미 삭제된 모듈 재삭제 시도 테스트"""
    # 첫 번째 삭제 시도 -> 성공 (soft delete)
    response_first = client.delete(
        f"/admin/modules/{test_module.module_id}",
        headers={"Authorization": f"Bearer {master_token}"}
    )
    assert response_first.status_code == 200
    data_first = response_first.json()
    assert data_first["resultCode"] == "SUCCESS"
    
    # 두 번째 삭제 시도 -> 이미 삭제되어 존재하지 않으므로 404 Not Found
    response_second = client.delete(
        f"/admin/modules/{test_module.module_id}",
        headers={"Authorization": f"Bearer {master_token}"}
    )
    assert response_second.status_code == 404
    data_second = response_second.json()
    assert data_second["resultCode"] == "FAILURE"
    assert data_second["message"] == "Module not found"
    assert data_second["error_code"] == "NOT_FOUND"
