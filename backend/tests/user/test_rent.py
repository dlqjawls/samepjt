import pytest
from datetime import datetime, timedelta

def create_valid_rent_request():
    """유효한 렌트 요청 데이터 생성"""
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

def register_and_login(client):
    """테스트용 사용자 등록 및 로그인 헬퍼 함수"""
    # Register
    register_payload = {
        "id": "rentuser",
        "password": "test1234",
        "email": "rent@example.com",
        "name": "렌트테스트",
        "phoneNum": "010-1234-5678",
        "address": "Seoul, Korea"
    }
    client.post("/auth/register", json=register_payload)

    # Login
    login_payload = {
        "id": "rentuser",
        "password": "test1234"
    }
    login_response = client.post("/auth/login", json=login_payload)
    return login_response.json()["data"]["access_token"]

# def test_create_rent(client):
#     """정상적인 렌트 생성 테스트"""
#     # Given: 로그인된 사용자
#     access_token = register_and_login(client)

#     # When: 유효한 렌트 요청
#     rent_request = create_valid_rent_request()
#     response = client.post(
#         "/user/rent",
#         json=rent_request,
#         headers={"Authorization": f"Bearer {access_token}"}
#     )

#     # Then: 응답 검증
#     assert response.status_code == 200
#     data = response.json()
#     assert data["resultCode"] == "SUCCESS"
#     assert "rent_id" in data["data"]
#     assert "vehicle_number" in data["data"]
#     assert isinstance(data["data"]["rent_id"], int)

# @pytest.mark.parametrize("option_quantity,expected_status,expected_message", [
#     (1, 200, "SUCCESS"),
#     (0, 422, "Validation error"),
#     (-1, 422, "Validation error"),
#     (999, 404, "Not enough available options")
# ])
# def test_create_rent_with_different_quantities(client, option_quantity, expected_status, expected_message):
#     """옵션 수량 변경에 따른 렌트 생성 테스트"""
#     # Given: 로그인된 사용자
#     access_token = register_and_login(client)
    
#     # When: 다양한 수량으로 렌트 요청
#     rent_request = create_valid_rent_request()
#     rent_request["selectedOptionTypes"][0]["quantity"] = option_quantity
    
#     response = client.post(
#         "/user/rent", 
#         json=rent_request,
#         headers={"Authorization": f"Bearer {access_token}"}
#     )

#     # Then: 응답 검증
#     assert response.status_code == expected_status
#     data = response.json()
    
#     if expected_status == 200:
#         assert data["resultCode"] == "SUCCESS"
#         assert "rent_id" in data["data"]
#     else:
#         assert data["resultCode"] == "FAILURE"
#         assert expected_message in data["message"]

# @pytest.mark.parametrize("coordinates,expected_status", [
#     ({"x": 12.313, "y": 32.3232}, 200),
#     ({"x": -180.1, "y": 32.3232}, 422),
#     ({"x": 180.1, "y": 32.3232}, 422),
#     ({"x": "invalid", "y": 32.3232}, 422),
#     ({"x": None, "y": 32.3232}, 422)
# ])
# def test_create_rent_with_different_coordinates(client, coordinates, expected_status):
#     """좌표값 유효성 테스트"""
#     # Given: 로그인된 사용자
#     access_token = register_and_login(client)
    
#     # When: 다양한 좌표값으로 렌트 요청
#     rent_request = create_valid_rent_request()
#     rent_request["autonomousArrivalPoint"] = coordinates
    
#     response = client.post(
#         "/user/rent",
#         json=rent_request,
#         headers={"Authorization": f"Bearer {access_token}"}
#     )

#     # Then: 응답 검증
#     assert response.status_code == expected_status
#     if expected_status == 200:
#         assert response.json()["resultCode"] == "SUCCESS"
#     else:
#         assert response.json()["resultCode"] == "FAILURE"

def test_create_rent_without_token(client):
    """인증 토큰 없이 렌트 생성 시도 테스트"""
    # When: 토큰 없이 렌트 요청
    response = client.post("/user/rent", json=create_valid_rent_request())
    print(response.json())
    # Then: 401 Unauthorized 응답 검증
    assert response.status_code == 401
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "authentication" in data["message"].lower()

def test_cancel_rent(client):
    """정상적인 렌트 취소 테스트"""
    # Given: 로그인된 사용자와 생성된 렌트
    access_token = register_and_login(client)
    
    rent_request = create_valid_rent_request()
    create_response = client.post(
        "/user/rent",
        json=rent_request,
        headers={"Authorization": f"Bearer {access_token}"}
    )
    rent_id = create_response.json()["data"]["rent_id"]
    
    # When: 렌트 취소
    cancel_response = client.delete(
        f"/user/rent/{rent_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # Then: 응답 검증
    assert cancel_response.status_code == 200
    data = cancel_response.json()
    assert data["resultCode"] == "SUCCESS"
    assert data["message"] == "Rent canceled successfully"
    assert data["data"]["rent_id"] == rent_id

def test_cancel_other_user_rent(client):
    """다른 사용자의 렌트 취소 시도 테스트"""
    # Given: 첫 번째 사용자의 렌트 생성
    first_user_token = register_and_login(client)
    rent_request = create_valid_rent_request()
    create_response = client.post(
        "/user/rent",
        json=rent_request,
        headers={"Authorization": f"Bearer {first_user_token}"}
    )
    rent_id = create_response.json()["data"]["rent_id"]

    # When: 두 번째 사용자로 첫 번째 사용자의 렌트 취소 시도
    register_payload = {
        "id": "otheruser",
        "password": "test1234",
        "email": "other@example.com",
        "name": "다른사용자",
        "phoneNum": "010-9999-8888",
        "address": "Busan, Korea"
    }
    client.post("/auth/register", json=register_payload)
    login_response = client.post("/auth/login", json={
        "id": "otheruser",
        "password": "test1234"
    })
    second_user_token = login_response.json()["data"]["access_token"]

    cancel_response = client.delete(
        f"/user/rent/{rent_id}",
        headers={"Authorization": f"Bearer {second_user_token}"}
    )

    # Then: 권한 없음 응답 검증
    assert cancel_response.status_code == 403
    data = cancel_response.json()
    assert data["resultCode"] == "FAILURE"
    assert "unauthorized" in data["message"].lower()

def test_cancel_nonexistent_rent(client):
    """존재하지 않는 렌트 취소 테스트"""
    # Given: 로그인된 사용자
    access_token = register_and_login(client)

    # When: 존재하지 않는 렌트 ID로 취소 시도
    response = client.delete(
        "/user/rent/99999",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # Then: 404 Not Found 응답 검증
    assert response.status_code == 404
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "not found" in data["message"].lower()

def test_cancel_already_canceled_rent(client):
    """이미 취소된 렌트 재취소 시도 테스트"""
    # Given: 로그인된 사용자와 취소된 렌트
    access_token = register_and_login(client)
    
    rent_request = create_valid_rent_request()
    create_response = client.post(
        "/user/rent",
        json=rent_request,
        headers={"Authorization": f"Bearer {access_token}"}
    )
    rent_id = create_response.json()["data"]["rent_id"]
    
    # 첫 번째 취소
    client.delete(
        f"/user/rent/{rent_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    # When: 두 번째 취소 시도
    second_cancel = client.delete(
        f"/user/rent/{rent_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # Then: 이미 취소됨 응답 검증
    assert second_cancel.status_code == 409
    data = second_cancel.json()
    assert data["resultCode"] == "FAILURE"
    assert "already canceled" in data["message"].lower()