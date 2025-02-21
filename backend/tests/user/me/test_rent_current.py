import pytest
from tests.helpers import register_and_login, create_test_rent
from app.core.jwt import jwt_handler

@pytest.fixture
def non_admin_token():
    return jwt_handler.create_token(2, role="user")[0]
  
@pytest.fixture
def current_rent_id(client, non_admin_token):
    """
    non_admin_token을 사용하여 /user/rent 엔드포인트로 실제 렌트 요청을 생성하고
    생성된 rent_id를 반환합니다.
    """
    return create_test_rent(client, non_admin_token)

def test_get_current_rent_success(client, non_admin_token, current_rent_id):
    """
    정상적인 현재 렌트 조회 테스트:
    - non_admin_token을 사용하여 실제 렌트 요청 생성 (current_rent_id 피스쳐에 의해)
    - /user/me/rent/current 엔드포인트 호출 시, 생성한 rent_id가 응답에 포함되어야 합니다.
    """
    response = client.get(
        "/api/user/me/rent/current",
        headers={"Authorization": f"Bearer {non_admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["resultCode"] == "SUCCESS"
    # 가장 최근의 요청으로 생성된 rent_id가 조회되어야 합니다.
    assert data["data"]["rent_id"] == current_rent_id

def test_get_current_rent_not_found(client):
    """
    현재 진행 중인 렌트가 없을 경우 200 응답을 검증합니다.
    """
    access_token = register_and_login(client, "testuser2", "test1234")

    response = client.get(
        "/api/user/me/rent/current",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["resultCode"] == "SUCCESS"
    assert data["data"] is None
def test_get_current_rent_without_token(client):
    """
    인증 토큰 없이 요청 시 401 Unauthorized 응답을 검증합니다.
    """
    response = client.get("/api/user/me/rent/current")
    assert response.status_code == 401

def test_get_current_rent_invalid_token(client):
    """
    잘못된 형식의 토큰으로 요청 시 401 Unauthorized 응답을 검증합니다.
    """
    response = client.get(
        "/api/user/me/rent/current",
        headers={"Authorization": "Bearer invalid.token.string"}
    )
    assert response.status_code == 401

# 새로운 통합 플로우 테스트: 렌트 신청 → 완료 → 재신청 검증
def test_current_rent_flow(client, non_admin_token):
    """
    통합 테스트:
    1. 렌트 신청 후 현재 진행 중인 렌트 조회 시 올바른 rent_id를 반환 (200)
    2. 렌트를 완료하면, 진행 중 렌트 조회 시 404를 반환
    3. 재신청 후, 진행 중 렌트 조회 시 새 rent_id 반환 (200)
    """
    # 1. 렌트 신청 → 현재 진행 중인 렌트 조회
    rent_id1 = create_test_rent(client, non_admin_token)
    response = client.get(
        "/api/user/me/rent/current",
        headers={"Authorization": f"Bearer {non_admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["resultCode"] == "SUCCESS"
    assert data["data"]["rent_id"] == rent_id1

    # 2. 렌트 완료 → 진행 중 렌트 조회 시 Null 반환
    response = client.post(
        f"/api/user/rent/{rent_id1}/complete",
        headers={"Authorization": f"Bearer {non_admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["resultCode"] == "SUCCESS"
    assert data["data"] is None

    response = client.get(
        "/api/user/me/rent/current",
        headers={"Authorization": f"Bearer {non_admin_token}"}
    )
    assert response.status_code == 404
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "진행 중인 렌트 정보가 존재하지 않습니다" in data["message"]

    # 3. 재렌트 신청 → 진행 중 렌트 조회 시 새 rent_id 반환
    rent_id2 = create_test_rent(client, non_admin_token)
    response = client.get(
        "/api/user/me/rent/current",
        headers={"Authorization": f"Bearer {non_admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["resultCode"] == "SUCCESS"
    assert data["data"]["rent_id"] == rent_id2
