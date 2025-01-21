import pytest

def test_admin_login_success(client):
    """
    (Success) 정상적인 관리자 로그인 테스트

    Given: 회원가입이 완료된 관리자가 있을 때
    When: 올바른 adminId와 adminPassword로 로그인 요청을 보내면
    Then: 응답 상태 코드 200과 "SUCCESS" 메시지를 반환하고, JWT 토큰이 포함되어야 한다.
    """

    # 로그인 요청
    response = client.post("/admin/login", json={
        "adminId": "admin",
        "adminPassword": "admin123"
    })

    json_response = response.json()

    assert response.status_code == 200
    assert json_response["resultCode"] == "SUCCESS"
    assert json_response["message"] == "Login successful"
    assert "token" in json_response  # JWT 토큰이 반환되어야 함


def test_login_invalid_admin(client):
    """
    (Fail) 존재하지 않는 관리자자 로그인 시 실패

    Given: 존재하지 않는 adminId가 있을 때
    When: 해당 adminId로 로그인 요청을 보내면
    Then: 응답 상태 코드 401과 "Admin ID does not exist" 오류 메시지를 반환해야 한다.
    """
    response = client.post("/admin/login", json={
        "adminId": "nonExistentAdmin",
        "adminPassword": "password123"
    })

    json_response = response.json()

    assert response.status_code == 401
    assert json_response["detail"]["resultCode"] == "FAILURE"
    assert any(error["field"] == "adminId" and error["message"] == "Admin ID does not exist"
               for error in json_response["detail"]["errors"])


def test_admin_login_wrong_password(client):
    """
    (Fail) 올바른 adminId지만 잘못된 비밀번호 입력 시 실패

    Given: 회원가입된 사용자가 있을 때
    When: 틀린 비밀번호로 로그인 요청을 보내면
    Then: 응답 상태 코드 401과 "Incorrect password" 오류 메시지를 반환해야 한다.
    """
    # 회원가입
    client.post("/admin/register", json={
        "adminId": "wrongPassAdmin",
        "adminPassword": "correctPass123",
        "adminEmail": "wrongpass@example.com",
        "adminName": "John Doe",
        "adminPhoneNum": "010-9876-5432",
        "adminAddress": "Unknown Street, City, Country"
    })

    # 잘못된 비밀번호 입력
    response = client.post("/admin/login", json={
        "adminId": "admin",
        "adminPassword": "wrongPass456"
    })

    json_response = response.json()
    
    assert response.status_code == 401
    assert json_response["detail"]["resultCode"] == "FAILURE"
    assert any(error["field"] == "adminPassword" and error["message"] == "Incorrect password"
               for error in json_response["detail"]["errors"])


def test_admin_login_empty_fields(client):
    """
    (Fail) adminId 또는 adminPassword가 비어있을 때 로그인 실패

    Given: adminId 또는 adminPassword 값이 없는 상태에서
    When: 빈 값으로 로그인 요청을 보내면
    Then: 응답 상태 코드 422와 FastAPI의 유효성 검사 오류가 발생해야 한다.
    """
    response = client.post("/admin/login", json={
        "adminId": "", # 빈 값
        "adminPassword": "password123"
    })

    assert response.status_code == 422  # FastAPI의 데이터 검증 오류

def test_admin_login_invalid_json_format(client):
    """
    (Fail) 잘못된 JSON 형식으로 로그인 요청 시 실패

    Given: 로그인 요청의 JSON 형식이 올바르지 않을 때
    When: 필수 JSON 필드가 누락되거나 형식이 잘못된 요청을 보내면
    Then: 응답 상태 코드 422와 유효성 검사 오류가 발생해야 한다.
    """
    response = client.post("/admin/login", json={
        "adminId": "validAdmin"
        # adminPassword 필드가 누락됨
    })

    assert response.status_code == 422  # FastAPI의 데이터 검증 오류
