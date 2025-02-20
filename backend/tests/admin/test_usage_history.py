import pytest
from fastapi.testclient import TestClient
from app.core.jwt import jwt_handler

# --- 토큰 생성용 Fixture ---
@pytest.fixture
def master_token():
    # JWTHandler의 create_token()은 (access_token, refresh_token)을 반환합니다.
    return jwt_handler.create_token(1, role="master")[0]

@pytest.fixture
def semi_admin_token():
    return jwt_handler.create_token(2, role="semi")[0]

@pytest.fixture
def non_admin_token():
    return jwt_handler.create_token(3, role="user")[0]

# --- 테스트 케이스 ---

def test_get_usage_history_success(client, master_token):
    """
    관리자 토큰으로 사용 이력 조회 시 올바른 응답을 받는지 확인합니다.
    """
    response = client.get(
        "/api/admin/usage-history?page=1&page_size=10",
        headers={"Authorization": f"Bearer {master_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["resultCode"] == "SUCCESS"
    # 응답 데이터에 pagination 및 usage_history 필드가 포함되어 있는지 확인합니다.
    assert "pagination" in data["data"]
    assert "usage_history" in data["data"]

def test_get_usage_history_include_deleted(client, master_token):
    """
    include_deleted 옵션으로 삭제된 항목도 포함하여 조회할 수 있는지 확인합니다.
    """
    response = client.get(
        "/api/admin/usage-history?page=1&page_size=10&include_deleted=true",
        headers={"Authorization": f"Bearer {master_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["resultCode"] == "SUCCESS"

def test_get_usage_history_unauthorized(client):
    """
    인증 없이 사용 이력을 조회할 경우 401 Unauthorized 응답을 받는지 확인합니다.
    """
    response = client.get("/api/admin/usage-history?page=1&page_size=10")
    assert response.status_code == 401

def test_get_usage_history_forbidden(client, non_admin_token):
    """
    일반 사용자 토큰을 사용하여 사용 이력을 조회할 경우 403 Forbidden 응답을 받는지 확인합니다.
    """
    response = client.get(
        "/api/admin/usage-history?page=1&page_size=10",
        headers={"Authorization": f"Bearer {non_admin_token}"}
    )
    assert response.status_code == 403 