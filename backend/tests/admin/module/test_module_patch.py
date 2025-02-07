import pytest
from datetime import datetime
from app.core.jwt import jwt_handler
from app.db.models.module import Module
from sqlmodel import Session, select
from app.utils.lut_constants import ItemStatus

@pytest.fixture
def master_token():
    """마스터 권한 토큰 생성"""
    return jwt_handler.create_token(1, role="master")[0]

@pytest.fixture
def semi_admin_token():
    """일반 관리자 권한 토큰 생성"""
    return jwt_handler.create_token(2, role="semi")[0]

@pytest.fixture
def test_module(session: Session):
    """테스트용 모듈 데이터 생성"""
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
    return module

def test_update_module_success(client, session, master_token, test_module):
    """✅ 정상적인 모듈 정보 업데이트 테스트"""
    # Given: 업데이트할 모듈 데이터
    update_data = {
        "module_type_id": 2,
    }

    # When: 마스터 권한으로 모듈 정보 업데이트 요청
    response = client.patch(
        f"/admin/modules/{test_module.module_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {master_token}"}
    )

    # Then: 응답 검증
    assert response.status_code == 200
    data = response.json()
    assert data["resultCode"] == "SUCCESS"
    assert data["message"] == "Module updated successfully"

    # Then: DB에 저장된 데이터 검증
    updated_module = session.exec(
        select(Module).where(Module.module_id == test_module.module_id)
    ).first()
    assert updated_module.module_type_id == update_data["module_type_id"]

def test_update_module_unauthorized(client, test_module, semi_admin_token):
    """❌ 권한 없는 사용자의 모듈 정보 업데이트 시도"""
    update_data = {
        "module_type_id": 2,
    }

    response = client.patch(
        f"/admin/modules/{test_module.module_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {semi_admin_token}"}
    )

    assert response.status_code == 403
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "Permission denied" in data["message"]

def test_update_nonexistent_module(client, master_token):
    """❌ 존재하지 않는 모듈 정보 업데이트 시도"""
    update_data = {
        "module_type_id": 2,
    }

    response = client.patch(
        "/admin/modules/99999",
        json=update_data,
        headers={"Authorization": f"Bearer {master_token}"}
    )

    assert response.status_code == 404
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "Module not found" in data["message"]

@pytest.mark.parametrize("invalid_module_type_id", [
    "PBV1234",  # 하이픈 없음
    "PBV-123",  # 숫자 3자리
    "PBV-12345",  # 숫자 5자리
    "ABC-1234",  # 잘못된 접두사
    "pbv-1234",  # 소문자
    "PBV-123A",  # 문자 포함
    " PBV-1234 "  # 앞뒤 공백
])
def test_update_module_invalid_module_type_id_format(client, master_token, test_module, invalid_module_type_id):
    """❌ 잘못된 형식의 모듈 타입 ID로 업데이트 시도"""
    update_data = {
        "module_type_id": invalid_module_type_id
    }

    response = client.patch(
        f"/admin/modules/{test_module.module_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {master_token}"}
    )

    assert response.status_code == 422
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "validation error" in data["message"].lower()

def test_update_module_without_token(client, test_module):
    """❌ 인증 토큰 없이 모듈 정보 업데이트 시도"""
    update_data = {
        "module_type_id": 2
    }

    response = client.patch(
        f"/admin/modules/{test_module.module_id}",
        json=update_data
    )

    assert response.status_code == 401
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "Authentication" in data["message"]
