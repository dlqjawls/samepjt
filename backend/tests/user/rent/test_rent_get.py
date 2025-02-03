import pytest
from typing import Dict
from datetime import datetime, timedelta

def create_valid_rent_request() -> Dict:
    """유효한 렌트 요청 데이터를 생성하는 함수"""
    return {
        "selectedOptionTypes": [
            {"optionTypeId": 1, "quantity": 1},
            {"optionTypeId": 2, "quantity": 1}
        ],
        "autonomousArrivalPoint": {"x": 12.313, "y": 32.3232},
        "autonomousDeparturePoint": {"x": 11.512, "y": 30.4531},
        "rentStartDate": (datetime.now() + timedelta(days=1)).isoformat(),
        "rentEndDate": (datetime.now() + timedelta(days=2)).isoformat()
    }

def register_and_login(client, user_id="rentuser") -> str:
    """테스트용 사용자 등록 및 로그인 후 access_token 반환"""
    register_payload = {
        "id": user_id,
        "password": "test1234",
        "email": f"{user_id}@example.com",
        "name": f"{user_id} Tester",
        "phoneNum": "010-1234-5678",
        "address": "Seoul, Korea"
    }
    client.post("/auth/register", json=register_payload)

    login_payload = {"id": user_id, "password": "test1234"}
    login_response = client.post("/auth/login", json=login_payload)
    return login_response.json()["data"]["access_token"]

def create_rent(client, access_token: str) -> int:
    """렌트 요청을 생성하고 rent_id 반환"""
    rent_request = create_valid_rent_request()
    response = client.post(
        "/user/rent",
        json=rent_request,
        headers={"Authorization": f"Bearer {access_token}"}
    )
    return response.json()["data"]["rent_id"]

# ✅ 정상적인 렌트 조회
def test_get_rent_success(client):
    """✅ 정상적인 렌트 조회 테스트"""
    access_token = register_and_login(client)
    rent_id = create_rent(client, access_token)

    response = client.get(
        f"/user/rent/{rent_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["resultCode"] == "SUCCESS"
    assert data["message"] == "Vehicle rent status retrieved successfully"
    assert "ETA" in data["data"]

# 🚫 다른 사용자의 렌트 조회 시도
def test_get_other_user_rent(client):
    """🚫 다른 사용자의 렌트 조회 시도 테스트"""
    first_user_token = register_and_login(client, "user1")
    rent_id = create_rent(client, first_user_token)

    second_user_token = register_and_login(client, "user2")
    response = client.get(
        f"/user/rent/{rent_id}",
        headers={"Authorization": f"Bearer {second_user_token}"}
    )

    assert response.status_code == 403
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "permission denie" in data["message"].lower()

# ❓ 존재하지 않는 렌트 조회
def test_get_nonexistent_rent(client):
    """❓ 존재하지 않는 렌트 조회 테스트"""
    access_token = register_and_login(client)

    response = client.get(
        "/user/rent/99999",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 404
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "not found" in data["message"].lower()

# ⚠️ 취소된 렌트 조회
def test_get_canceled_rent(client):
    """⚠️ 취소된 렌트 조회 시도 테스트"""
    access_token = register_and_login(client)
    rent_id = create_rent(client, access_token)

    # 렌트 취소
    client.delete(
        f"/user/rent/{rent_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # 취소된 렌트 조회 시도
    response = client.get(
        f"/user/rent/{rent_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 409
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "rent already canceled or completed" in data["message"].lower()

# # 🛑 완료된 렌트 조회
# def test_get_completed_rent(client):
#     """🛑 완료된 렌트 조회 테스트"""
#     access_token = register_and_login(client)
#     rent_id = create_rent(client, access_token)


# ❌ 인증 없이 렌트 조회
def test_get_rent_without_token(client):
    """❌ 인증 없이 렌트 조회 시도 테스트"""
    response = client.get("/user/rent/1")
    
    assert response.status_code == 401
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "authentication" in data["message"].lower()

# 🚨 잘못된 형식의 렌트 ID로 조회 시도
@pytest.mark.parametrize("invalid_rent_id", ["abc", -1, 0, None])
def test_get_rent_invalid_id(client, invalid_rent_id):
    """🚨 잘못된 형식의 렌트 ID로 조회 시도 테스트"""
    access_token = register_and_login(client)

    response = client.get(
        f"/user/rent/{invalid_rent_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 422  # FastAPI의 Pydantic 유효성 검사 실패
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "validation error" in data["message"].lower()
