import pytest

def test_register_success(client):
    """정상적인 회원가입 테스트"""
    # Given: 유효한 회원가입 요청 데이터
    payload = {
        "id": "testuser",
        "password": "test1234",
        "email": "test@example.com",
        "name": "테스트유저",
        "phoneNum": "010-1234-5678", 
        "address": "Seoul, Korea"
    }

    # When: 회원가입 API 호출
    response = client.post("/auth/register", json=payload)
    
    # Then: 응답 검증
    assert response.status_code == 200
    data = response.json()
    assert data["resultCode"] == "SUCCESS"
    assert data["message"] == "User registered successfully"
    assert not data.get("detail")  # 에러 상세정보 없음

def test_register_duplicate_id(client):
    """중복 ID 회원가입 시도 테스트"""
    # Given: 이미 등록된 사용자 정보
    payload = {
        "id": "dupuser",
        "password": "test1234",
        "email": "dup@example.com",
        "name": "중복테스트",
        "phoneNum": "010-1111-2222",
        "address": "Seoul, Korea"
    }
    
    # 첫 번째 회원가입
    client.post("/auth/register", json=payload)

    # When: 같은 ID로 회원가입 시도
    response = client.post("/auth/register", json=payload)

    # Then: 400 Bad Request 응답 검증
    assert response.status_code == 400
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert data["message"] == "User ID already exists"
    assert data["detail"]["id"] == payload["id"]

def test_register_duplicate_email(client):
    """중복 이메일 회원가입 시도 테스트"""
    # Given: 이미 등록된 사용자 정보
    payload = {
        "id": "uniqueuser",
        "password": "test1234",
        "email": "dup@example.com",
        "name": "중복테스트",
        "phoneNum": "010-1111-2222",
        "address": "Seoul, Korea"
    }
    
    # 첫 번째 회원가입
    client.post("/auth/register", json=payload)

    # When: 같은 이메일로 회원가입 시도
    payload["id"] = "anotheruser"
    response = client.post("/auth/register", json=payload)

    # Then: 400 Bad Request 응답 검증
    assert response.status_code == 400
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert data["message"] == "Email is already exists"
    assert data["detail"]["email"] == payload["email"]

def test_register_invalid_data(client):
    """잘못된 데이터로 회원가입 시도 테스트"""
    # Given: 유효하지 않은 회원가입 데이터
    payload = {
        "id": "t",  # 3글자 미만
        "password": "123",  # 6글자 미만
        "email": "invalid-email",  # 잘못된 이메일 형식
        "name": "",  # 빈 이름
        "phoneNum": "123", 
        "address": ""  # 빈 주소
    }

    # When: 회원가입 API 호출
    response = client.post("/auth/register", json=payload)

    # Then: 422 Unprocessable Entity 응답 검증
    assert response.status_code == 422
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "validation" in data["message"].lower()
    assert data["detail"]  # 검증 오류 상세정보 존재