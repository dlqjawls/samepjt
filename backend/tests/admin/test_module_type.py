import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from app.core.jwt import jwt_handler

@pytest.fixture
def master_token():
    """마스터 권한 토큰 생성"""
    return jwt_handler.create_token(1, role="master")[0]

@pytest.fixture
def semi_admin_token():
    """일반 관리자 권한 토큰 생성"""
    return jwt_handler.create_token(2, role="semi")[0]
  
@pytest.fixture
def non_admin_token():
    return jwt_handler.create_token(2, role="user")[0]

def test_get_module_types_success(client: TestClient, master_token):
    headers = {"Authorization": f"Bearer {master_token}"}
    response = client.get("/api/admin/module-types", headers=headers)
    assert response.status_code == 200
    assert response.json()["resultCode"] == "SUCCESS"
    assert response.json()["data"]["module_types"]

def test_get_module_types_unauthorized(client: TestClient, non_admin_token):
    headers = {"Authorization": f"Bearer {non_admin_token}"}
    response = client.get("/api/admin/module-types", headers=headers)
    assert response.status_code == 403
    assert response.json()["resultCode"] == "FAILURE"
    assert response.json()["message"] == "Permission denied"

def test_get_module_types_empty(client: TestClient, master_token, session):
    # 모듈 타입 테이블 초기화
    session.exec(text("DELETE FROM lut_module_type"))
    session.commit()

    headers = {"Authorization": f"Bearer {master_token}"}
    response = client.get("/api/admin/module-types", headers=headers)
    assert response.status_code == 200
    assert response.json()["resultCode"] == "SUCCESS"
    assert response.json()["data"]["module_types"] == []