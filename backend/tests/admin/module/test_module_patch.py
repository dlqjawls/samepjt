import pytest
from datetime import datetime
from app.core.jwt import jwt_handler
from app.db.models.module import Module
from sqlmodel import Session, select
from app.utils.lut_constants import ModuleType
from tests.helpers import master_token, semi_admin_token, user_token, create_dummy_modules


def test_update_module_success(client, session, master_token, create_dummy_modules):
    """정상적인 모듈 정보 업데이트 테스트"""
    # 더미 모듈 1건 생성
    modules = create_dummy_modules(1)
    module = modules[0]
    update_data = {
        "module_type_id": ModuleType.MEDIUM.ID, # 모듈 타입 업데이트
    }
    response = client.patch(
        f"/api/admin/modules/{module.module_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {master_token}"}
    )
    # 응답 검증
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["resultCode"] == "SUCCESS"
    assert data["message"] == "Module updated successfully"
    
    # DB에 변경 내용 반영 여부 검증
    updated_module = session.get(Module, module.module_id)
    assert updated_module.module_type_id == ModuleType.MEDIUM.ID

def test_update_module_unauthorized(client, create_dummy_modules):
    """인증 토큰 없이 모듈 정보 업데이트 시도 테스트"""
    modules = create_dummy_modules(1)
    module = modules[0]
    update_data = {
        "module_type_id": ModuleType.MEDIUM.ID
    }
    response = client.patch(
        f"/api/admin/modules/{module.module_id}",
        json=update_data
    )
    assert response.status_code == 401

def test_update_module_forbidden(client, create_dummy_modules, user_token):
    """비관리자 토큰으로 모듈 정보 업데이트 시도 테스트"""
    modules = create_dummy_modules(1)
    module = modules[0]
    update_data = {
        "module_type_id": ModuleType.MEDIUM.ID
    }
    response = client.patch(
        f"/api/admin/modules/{module.module_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 403

def test_update_nonexistent_module(client, master_token):
    """존재하지 않는 모듈 정보 업데이트 시도 테스트"""
    update_data = {
        "module_type_id": ModuleType.MEDIUM.ID
    }
    response = client.patch(
        "/api/admin/modules/99999",  # 존재하지 않는 모듈 ID
        json=update_data,
        headers={"Authorization": f"Bearer {master_token}"}
    )
    assert response.status_code == 404
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "Module not found" in data["message"]

@pytest.mark.parametrize("invalid_module_id", ["abc", -1, 0])
def test_update_module_invalid_id(client, master_token, invalid_module_id):
    """잘못된 형식의 모듈 ID로 업데이트 시도 테스트"""
    update_data = {
        "module_type_id": ModuleType.MEDIUM.ID
    }
    response = client.patch(
        f"/api/admin/modules/{invalid_module_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {master_token}"}
    )
    # Pydantic 유효성 검사 실패 시 422 에러 발생
    assert response.status_code == 422

@pytest.mark.parametrize("invalid_module_type_id", [
    "0",
    "-1",
    "a",
    " ",
    "*",
])
def test_update_module_invalid_module_type_id(client, master_token, create_dummy_modules, invalid_module_type_id):
    """잘못된 형식의 모듈 타입 업데이트 시도 테스트"""
    modules = create_dummy_modules(1)
    module = modules[0]
    update_data = {
        "module_type_id": invalid_module_type_id
    }

    response = client.patch(
        f"/api/admin/modules/{module.module_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {master_token}"}
    )

    assert response.status_code == 422
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    

@pytest.mark.parametrize("non_existing_module_type_id", [
    "99999",
    "100000"
])
def test_update_module_non_existing_module_type_id(client, master_token, create_dummy_modules, non_existing_module_type_id):
    """존재하지 않는 모듈 타입 업데이트 시도 테스트"""
    modules = create_dummy_modules(1)
    module = modules[0]
    update_data = {
        "module_type_id": non_existing_module_type_id
    }

    response = client.patch(
        f"/api/admin/modules/{module.module_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {master_token}"}
    )

    assert response.status_code == 404
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    