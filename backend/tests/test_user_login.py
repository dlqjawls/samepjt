import pytest

def test_login_success(client):
    """
    ✅ 정상적인 로그인 테스트

    Given: 회원가입이 완료된 사용자가 있을 때
    When: 올바른 userId와 userPassword로 로그인 요청을 보내면
    Then: 응답 상태 코드 200과 "SUCCESS" 메시지를 반환하고, JWT 토큰이 포함되어야 한다.
    """
    # ✅ 1. 테스트를 위한 회원가입
    client.post("/user/register", json={
        "userId": "testUser",
        "userPassword": "password123",
        "userEmail": "test@example.com",
        "userName": "John Doe",
        "userPhoneNum": "010-1234-5678",
        "userAddress": "123 Main St, City, Country"
    })

    # ✅ 2. 로그인 요청
    response = client.post("/user/login", json={
        "userId": "testUser",
        "userPassword": "password123"
    })

    json_response = response.json()
    print(json_response)  # 응답 확인

    assert response.status_code == 200
    assert json_response["resultCode"] == "SUCCESS"
    assert json_response["message"] == "Login successful"
    assert "token" in json_response  # JWT 토큰이 반환되어야 함


def test_login_invalid_user(client):
    """
    ❌ 존재하지 않는 사용자 로그인 시 실패

    Given: 존재하지 않는 userId가 있을 때
    When: 해당 userId로 로그인 요청을 보내면
    Then: 응답 상태 코드 401과 "User ID does not exist" 오류 메시지를 반환해야 한다.
    """
    response = client.post("/user/login", json={
        "userId": "nonExistentUser",
        "userPassword": "password123"
    })

    json_response = response.json()
    print(json_response)  # 응답 확인

    assert response.status_code == 401
    assert json_response["detail"]["resultCode"] == "FAILURE"
    assert any(error["field"] == "userId" and error["message"] == "User ID does not exist"
               for error in json_response["detail"]["errors"])


def test_login_wrong_password(client):
    """
    ❌ 올바른 userId지만 잘못된 비밀번호 입력 시 실패

    Given: 회원가입된 사용자가 있을 때
    When: 틀린 비밀번호로 로그인 요청을 보내면
    Then: 응답 상태 코드 401과 "Incorrect password" 오류 메시지를 반환해야 한다.
    """
    # ✅ 회원가입
    client.post("/user/register", json={
        "userId": "wrongPassUser",
        "userPassword": "correctPass123",
        "userEmail": "wrongpass@example.com",
        "userName": "John Doe",
        "userPhoneNum": "010-9876-5432",
        "userAddress": "Unknown Street, City, Country"
    })

    # ❌ 잘못된 비밀번호 입력
    response = client.post("/user/login", json={
        "userId": "wrongPassUser",
        "userPassword": "wrongPass456"
    })

    json_response = response.json()
    print(json_response)  # 응답 확인

    assert response.status_code == 401
    assert json_response["detail"]["resultCode"] == "FAILURE"
    assert any(error["field"] == "userPassword" and error["message"] == "Incorrect password"
               for error in json_response["detail"]["errors"])


def test_login_empty_fields(client):
    """
    ❌ userId 또는 userPassword가 비어있을 때 로그인 실패

    Given: userId 또는 userPassword 값이 없는 상태에서
    When: 빈 값으로 로그인 요청을 보내면
    Then: 응답 상태 코드 422와 FastAPI의 유효성 검사 오류가 발생해야 한다.
    """
    response = client.post("/user/login", json={
        "userId": "",
        "userPassword": "password123"
    })

    json_response = response.json()
    print(json_response)  # 응답 확인

    assert response.status_code == 422  # FastAPI가 자동으로 422 반환


def test_login_invalid_json_format(client):
    """
    ❌ 잘못된 JSON 형식으로 로그인 요청 시 실패

    Given: 로그인 요청의 JSON 형식이 올바르지 않을 때
    When: 필수 JSON 필드가 누락되거나 형식이 잘못된 요청을 보내면
    Then: 응답 상태 코드 422와 유효성 검사 오류가 발생해야 한다.
    """
    response = client.post("/user/login", json={
        "userId": "validUser"
        # userPassword 필드가 누락됨
    })

    json_response = response.json()
    print(json_response)  # 응답 확인

    assert response.status_code == 422  # FastAPI의 데이터 검증 오류
