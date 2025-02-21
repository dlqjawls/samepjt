import pytest
from tests.helpers import create_test_rent, register_and_login

# ✅ 정상적인 렌트 취소
def test_cancel_rent_success(client):
    """✅ 정상적인 렌트 취소 테스트"""
    access_token = register_and_login(client)
    rent_id = create_test_rent(client, access_token)

    response = client.delete(
        f"/api/user/rent/{rent_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["resultCode"] == "SUCCESS"
    assert data["message"] == "Rent canceled successfully"
    assert data["data"]["rent_id"] == rent_id

# 🚫 다른 사용자의 렌트 취소 시도
def test_cancel_other_user_rent(client):
    """🚫 다른 사용자의 렌트 취소 시도 테스트"""
    first_user_token = register_and_login(client, "user1")
    rent_id = create_test_rent(client, first_user_token)

    second_user_token = register_and_login(client, "user2")
    response = client.delete(
        f"/api/user/rent/{rent_id}",
        headers={"Authorization": f"Bearer {second_user_token}"}
    )

    assert response.status_code == 403
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "permission denied" in data["message"].lower()

# ❓ 존재하지 않는 렌트 취소
def test_cancel_nonexistent_rent(client):
    """❓ 존재하지 않는 렌트 취소 테스트"""
    access_token = register_and_login(client)

    response = client.delete(
        "/user/rent/99999",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 404
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "not found" in data["message"].lower()

# ⚠️ 이미 취소된 렌트 재취소
def test_cancel_already_canceled_rent(client):
    """⚠️ 이미 취소된 렌트 재취소 시도 테스트"""
    access_token = register_and_login(client)
    rent_id = create_test_rent(client, access_token)

    # 첫 번째 취소
    client.delete(
        f"/api/user/rent/{rent_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # 두 번째 취소 시도
    response = client.delete(
        f"/api/user/rent/{rent_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 409
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "rent already completed or canceled" in data["message"].lower()

# ❌ 인증 없이 렌트 취소
def test_cancel_rent_without_token(client):
    """❌ 인증 없이 렌트 취소 시도 테스트"""
    response = client.delete("/user/rent/1")
    
    assert response.status_code == 401
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "authentication" in data["message"].lower()

# 🛑 완료된 렌트 취소 시도
# def test_cancel_completed_rent(client):
#     """🛑 완료된 렌트 취소 시도 테스트"""
#     access_token = register_and_login(client)
#     rent_id = create_rent(client, access_token)


# 🚨 잘못된 형식의 렌트 ID로 취소 시도
@pytest.mark.parametrize("invalid_rent_id", ["abc", -1, 0, None])
def test_cancel_rent_invalid_id(client, invalid_rent_id):
    """🚨 잘못된 형식의 렌트 ID로 취소 시도 테스트"""
    access_token = register_and_login(client)

    response = client.delete(
        f"/api/user/rent/{invalid_rent_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 422  # FastAPI의 Pydantic 유효성 검사 실패
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "validation error" in data["message"].lower()
