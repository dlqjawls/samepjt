import pytest
from tests.helpers import create_valid_rent_request, register_and_login

def test_create_rent_success(client):
    """✅ 정상적인 렌트 생성 테스트"""
    access_token = register_and_login(client)

    rent_request = create_valid_rent_request()
    response = client.post(
        "/user/rent",
        json=rent_request,
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["resultCode"] == "SUCCESS"
    assert "rent_id" in data["data"]
    assert "vehicle_number" in data["data"]
    assert isinstance(data["data"]["rent_id"], int)

@pytest.mark.parametrize("option_quantity,expected_status,expected_message", [
    (1, 200, "SUCCESS"),
    (0, 422, "Validation error"),
    (-1, 422, "Validation error"),
    (999, 404, "Not enough available options")
])
def test_create_rent_with_different_quantities(client, option_quantity, expected_status, expected_message):
    """🔄 옵션 수량 변경에 따른 렌트 생성 테스트"""
    access_token = register_and_login(client)
    
    rent_request = create_valid_rent_request()
    rent_request["selectedOptionTypes"][0]["quantity"] = option_quantity
    
    response = client.post(
        "/user/rent", 
        json=rent_request,
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == expected_status
    data = response.json()
    
    if expected_status == 200:
        assert data["resultCode"] == "SUCCESS"
        assert "rent_id" in data["data"]
    else:
        assert data["resultCode"] == "FAILURE"
        assert expected_message in data["message"]

@pytest.mark.parametrize("coordinates,expected_status", [
    ({"x": 12.313, "y": 32.3232}, 200),
    ({"x": -180.1, "y": 32.3232}, 422),
    ({"x": 180.1, "y": 32.3232}, 422),
    ({"x": "invalid", "y": 32.3232}, 422),
    ({"x": None, "y": 32.3232}, 422)
])
def test_create_rent_with_invalid_coordinates(client, coordinates, expected_status):
    """🗺️ 좌표값 유효성 테스트"""
    access_token = register_and_login(client)
    
    rent_request = create_valid_rent_request()
    rent_request["autonomousArrivalPoint"] = coordinates
    
    response = client.post(
        "/user/rent",
        json=rent_request,
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == expected_status
    if expected_status == 200:
        assert response.json()["resultCode"] == "SUCCESS"
    else:
        assert response.json()["resultCode"] == "FAILURE"

def test_create_rent_without_token(client):
    """❌ 인증 토큰 없이 렌트 생성 시도 테스트"""
    response = client.post("/user/rent", json=create_valid_rent_request())

    assert response.status_code == 401
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "authentication" in data["message"].lower()
