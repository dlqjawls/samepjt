import pytest

def test_login_success(client):
    """정상적인 로그인 테스트"""
    # Given: 회원가입된 사용자
    register_payload = {
        "id": "loginuser",
        "password": "test1234",
        "email": "login@example.com",
        "name": "로그인테스트",
        "phoneNum": "010-1234-5678",
        "address": "Seoul, Korea"
    }
    client.post("/auth/register", json=register_payload)

    # When: 로그인 시도
    login_payload = {
        "id": "loginuser",
        "password": "test1234"
    }
    response = client.post("/auth/login", json=login_payload)

    # Then: 응답 검증
    assert response.status_code == 200
    data = response.json()
    assert data["resultCode"] == "SUCCESS"
    assert "data" in data
    assert "access_token" in data["data"]
    assert "refresh_token" in data["data"]

def test_login_invalid_credentials(client):
    """잘못된 인증 정보로 로그인 시도 테스트"""
    # When: 존재하지 않는 사용자로 로그인 시도
    response = client.post("/auth/login", json={
        "id": "nonexistent",
        "password": "wrongpass"
    })

    # Then: 401 Unauthorized 응답 검증
    assert response.status_code == 401
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "Invalid credentials" in data["message"]

def test_login_wrong_password(client):
    """잘못된 비밀번호로 로그인 시도 테스트"""
    # Given: 회원가입된 사용자
    register_payload = {
        "id": "passuser",
        "password": "correctpass",
        "email": "pass@example.com",
        "name": "비밀번호테스트",
        "phoneNum": "010-5555-6666",
        "address": "Busan, Korea"
    }
    client.post("/auth/register", json=register_payload)

    # When: 잘못된 비밀번호로 로그인 시도
    response = client.post("/auth/login", json={
        "id": "passuser",
        "password": "wrongpass"
    })

    # Then: 401 Unauthorized 응답 검증
    assert response.status_code == 401
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "Invalid credentials" in data["message"]

def test_login_invalid_data(client):
    """유효하지 않은 데이터로 로그인 시도 테스트"""
    # When: 형식이 맞지 않는 데이터로 로그인 시도
    response = client.post("/auth/login", json={
        "id": "t",  # 3글자 미만
        "password": "123"  # 6글자 미만
    })

    # Then: 422 Unprocessable Entity 응답 검증
    assert response.status_code == 422
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "validation" in data["message"].lower()
    assert data["detail"]  # 검증 오류 상세정보 존재