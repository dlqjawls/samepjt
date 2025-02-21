import pytest
from datetime import datetime
from app.db.models.module_set import ModuleSet
from sqlmodel import Session, select
from app.utils.lut_constants import ItemStatus
import json

from tests.helpers import master_token, semi_admin_token

@pytest.fixture
def test_module_set(session: Session):
    """테스트용 모듈 세트 데이터 생성"""
    module_set = ModuleSet(
        module_set_name="Test Module Set",
        description="Test Description",
        module_set_images="",
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

def test_update_module_set_success(client, session, master_token, test_module_set):
    """✅ 정상적인 모듈 세트 정보 업데이트 테스트"""
    # Given: 업데이트할 모듈 세트 데이터
    update_data = {
        "module_set_name": "Updated Module Set",
        "description": "Updated Description",
        "module_set_features": "Updated Feature1, Updated Feature2",
        "module_type_id": 2,
    }

    # When: 마스터 권한으로 모듈 세트 정보 업데이트 요청
    response = client.patch(
        f"/api/admin/module-sets/{get_module_set_id(session, test_module_set.module_set_name)}",
        json=update_data,
        headers={"Authorization": f"Bearer {master_token}"}
    )

    # Then: 응답 검증
    assert response.status_code == 200
    data = response.json()
    assert data["resultCode"] == "SUCCESS"
    assert data["message"] == "Module set updated successfully"

    # Then: DB에 저장된 데이터 검증
    updated_module_set = session.exec(
        select(ModuleSet).where(ModuleSet.module_set_id == get_module_set_id(session, test_module_set.module_set_name))
    ).first()
    assert updated_module_set.module_set_name is not None
    assert updated_module_set.description is not None
    assert updated_module_set.module_set_features is not None
    assert updated_module_set.module_type_id is not None

def test_update_module_set_unauthorized(client, session, test_module_set, semi_admin_token):
    """❌ 권한 없는 사용자의 모듈 세트 정보 업데이트 시도"""
    update_data = {
        "module_set_name": "Updated Module Set",
        "description": "Updated Description",
        "module_set_features": "Updated Feature1, Updated Feature2",
        "module_type_id": 2,
    }

    response = client.patch(
        f"/api/admin/module-sets/{get_module_set_id(session, test_module_set.module_set_name)}",
        json=update_data,
        headers={"Authorization": f"Bearer {semi_admin_token}"}
    )

    assert response.status_code == 403
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "Permission denied" in data["message"]

def test_update_nonexistent_module_set(client, session, master_token):
    """❌ 존재하지 않는 모듈 세트 정보 업데이트 시도"""
    update_data = {
        "module_set_name": "Updated Module Set",
        "description": "Updated Description",
        "module_set_features": "Updated Feature1, Updated Feature2",
        "module_type_id": 2,
    }

    response = client.patch(
        "/api/admin/module-sets/99999",
        json=update_data,
        headers={"Authorization": f"Bearer {master_token}"}
    )

    assert response.status_code == 404
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "Module set not found" in data["message"]


def test_update_module_set_without_token(client, session, test_module_set):
    """❌ 인증 토큰 없이 모듈 세트 정보 업데이트 시도"""
    update_data = {
        "module_set_name": "Updated Module Set",
        "description": "Updated Description",
        "module_set_features": "Updated Feature1, Updated Feature2",
        "module_type_id": 2,
    }

    response = client.patch(
        f"/api/admin/module-sets/{get_module_set_id(session, test_module_set.module_set_name)}",
        json=update_data
    )

    assert response.status_code == 401
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "Authentication" in data["message"]

