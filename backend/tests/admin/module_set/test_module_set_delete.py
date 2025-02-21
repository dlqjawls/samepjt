import pytest
from sqlmodel import Session, select
from app.db.models.module_set import ModuleSet
from datetime import datetime

from tests.helpers import master_token, semi_admin_token


@pytest.fixture
def test_module_set(session: Session):
    """테스트용 모듈 세트 데이터 생성"""
    module_set = ModuleSet(
        module_set_name="Test Module Set",
        description="Test Description",
        module_set_features="Feature1, Feature2",
        module_type_id=1,
        created_by=1,
        updated_by=1,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    session.add(module_set)
    session.commit()
    session.refresh(module_set)
    return module_set

def get_module_set_id(session: Session, module_set_name: str) -> int:
    """모듈 세트 ID 조회"""
    module_set = session.exec(select(ModuleSet).where(ModuleSet.module_set_name == module_set_name)).first()
    if not module_set or not module_set.module_set_id:
        raise ValueError(f"Module set with name {module_set_name} not found")
    return module_set.module_set_id
  

def test_delete_module_set_success(client, session, master_token, test_module_set):
    """✅ 모듈 세트 삭제 성공 테스트"""
    response = client.delete( 
        f"/api/admin/module-sets/{get_module_set_id(session, test_module_set.module_set_name)}",
        headers={"Authorization": f"Bearer {master_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["resultCode"] == "SUCCESS"
    assert data["message"] == "Module set deleted successfully"

def test_delete_module_set_not_found(client, master_token):
    """❌ 존재하지 않는 모듈 세트 삭제 시도 테스트"""
    response = client.delete(
        "/admin/module-sets/9999",  # 존재하지 않는 ID
        headers={"Authorization": f"Bearer {master_token}"}
    )

    assert response.status_code == 404
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert data["message"] == "Module set not found"
    assert data["error_code"] == "NOT_FOUND"

# 추가: 인증 토큰 없이 모듈 세트 삭제 시도 테스트
def test_delete_module_set_without_token(client, session, test_module_set):
    """❌ 인증 토큰 없이 모듈 세트 삭제 시도 테스트"""
    response = client.delete(f"/admin/module-sets/{get_module_set_id(session, test_module_set.module_set_name)}")
    assert response.status_code == 401
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    # 에러 메시지에 인증 관련 내용이 포함된 것을 확인
    assert "authentication" in data["message"].lower()

# 추가: 일반 관리자(권한 부족) 토큰으로 옵션 삭제 시도 테스트
def test_delete_module_set_with_non_master_token(client, session, test_module_set, semi_admin_token):
    """❌ 일반 관리자(권한 부족) 토큰으로 모듈 세트 삭제 시도 테스트"""
    response = client.delete(
        f"/api/admin/module-sets/{get_module_set_id(session, test_module_set.module_set_name)}",
        headers={"Authorization": f"Bearer {semi_admin_token}"}
    )
    assert response.status_code == 403
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    # 에러 메시지에 권한 거부 관련 내용이 포함된 것을 확인
    assert "permission denied" in data["message"].lower()

# 추가: 잘못된 형식의 모듈 세트 ID로 삭제 시도 테스트
@pytest.mark.parametrize("invalid_module_set_id", ["abc", -1, 0])
def test_delete_module_set_invalid_id(client, master_token, invalid_module_set_id):
    """🚨 잘못된 형식의 모듈 세트 ID로 삭제 시도 테스트"""
    response = client.delete(
        f"/api/admin/module-sets/{invalid_module_set_id}",
        headers={"Authorization": f"Bearer {master_token}"}
    )
    assert response.status_code == 422    
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    # 메시지에 검증 오류 상세 내용(예: "value is not a valid integer") 또는 "validation" 키워드가 포함되는지 확인
    assert "value is not a valid integer" in str(data["detail"]).lower() or "validation" in data["message"].lower()

# 추가: 이미 삭제된 옵션 재삭제 시도 테스트
def test_delete_module_set_already_deleted(client, session, master_token, test_module_set):
    """✅ 이미 삭제된 모듈 세트 재삭제 시도 테스트"""
    # 첫 번째 삭제 시도 -> 성공 (soft delete)
    response_first = client.delete(
        f"/api/admin/module-sets/{get_module_set_id(session, test_module_set.module_set_name)}",
        headers={"Authorization": f"Bearer {master_token}"}
    )
    assert response_first.status_code == 200
    data_first = response_first.json()
    assert data_first["resultCode"] == "SUCCESS"
    
    # 두 번째 삭제 시도 -> 이미 삭제되어 존재하지 않으므로 404 Not Found
    response_second = client.delete(
        f"/api/admin/module-sets/{get_module_set_id(session, test_module_set.module_set_name)}",
        headers={"Authorization": f"Bearer {master_token}"}
    )
    assert response_second.status_code == 404
    data_second = response_second.json()
    assert data_second["resultCode"] == "FAILURE"
    assert data_second["error_code"] == "NOT_FOUND"
