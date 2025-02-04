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

# ✅ 정상적인 렌트 완료
def test_complete_rent_success(client):
    """✅ 정상적인 렌트 완료 테스트"""
    access_token = register_and_login(client)
    rent_id = create_rent(client, access_token)

    response = client.post(
        f"/user/rent/{rent_id}/complete",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["resultCode"] == "SUCCESS"
    assert data["message"] == "Rental completed successfully"
    assert data["data"]["rent_id"] == rent_id
    assert isinstance(data["data"]["total_mileage"], float)
    assert isinstance(data["data"]["usage_duration"], int)
    assert isinstance(data["data"]["estimated_payback_amount"], float)

# 🚫 다른 사용자의 렌트 완료 시도
def test_complete_other_user_rent(client):
    """🚫 다른 사용자의 렌트 완료 시도 테스트"""
    first_user_token = register_and_login(client, "user1")
    rent_id = create_rent(client, first_user_token)

    second_user_token = register_and_login(client, "user2")
    response = client.post(
        f"/user/rent/{rent_id}/complete",
        headers={"Authorization": f"Bearer {second_user_token}"}
    )

    assert response.status_code == 403
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "permission denied" in data["message"].lower()

# ❓ 존재하지 않는 렌트 완료
def test_complete_nonexistent_rent(client):
    """❓ 존재하지 않는 렌트 완료 테스트"""
    access_token = register_and_login(client)

    response = client.post(
        "/user/rent/99999/complete",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 404
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "not found" in data["message"].lower()

# ⚠️ 이미 완료된 렌트 재완료
def test_complete_already_completed_rent(client):
    """⚠️ 이미 완료된 렌트 재완료 시도 테스트"""
    access_token = register_and_login(client)
    rent_id = create_rent(client, access_token)

    # 첫 번째 완료
    client.post(
        f"/user/rent/{rent_id}/complete",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # 두 번째 완료 시도
    response = client.post(
        f"/user/rent/{rent_id}/complete",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 409
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "already completed" in data["message"].lower()

# ⚠️ 취소된 렌트 완료 시도
def test_complete_canceled_rent(client):
    """⚠️ 취소된 렌트 완료 시도 테스트"""
    access_token = register_and_login(client)
    rent_id = create_rent(client, access_token)

    # 렌트 취소
    client.delete(
        f"/user/rent/{rent_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # 취소된 렌트 완료 시도
    response = client.post(
        f"/user/rent/{rent_id}/complete",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 409
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "rent already completed or canceled" in data["message"].lower()

# ❌ 인증 없이 렌트 완료
def test_complete_rent_without_token(client):
    """❌ 인증 없이 렌트 완료 시도 테스트"""
    response = client.post("/user/rent/1/complete")
    
    assert response.status_code == 401
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "authentication" in data["message"].lower()

# 🚨 잘못된 형식의 렌트 ID로 완료 시도
@pytest.mark.parametrize("invalid_rent_id", ["abc", -1, 0, None])
def test_complete_rent_invalid_id(client, invalid_rent_id):
    """🚨 잘못된 형식의 렌트 ID로 완료 시도 테스트"""
    access_token = register_and_login(client)

    response = client.post(
        f"/user/rent/{invalid_rent_id}/complete",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 422
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "validation error" in data["message"].lower()
