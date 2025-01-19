import pytest

def test_register_user_success(client):
    """
    ✅ 정상적인 회원가입 테스트

    Given: 유효한 사용자 정보가 주어졌을 때
    When: 회원가입 API(`/user/register`)에 유효한 정보를 포함하여 POST 요청을 보내면
    Then: 응답 상태 코드 200과 "SUCCESS" 메시지를 반환해야 한다.
    """
    response = client.post("/user/register", json={
        "userId": "newUser123",
        "userPassword": "password123",
        "userEmail": "newuser@example.com",
        "userName": "John Doe",
        "userPhoneNum": "010-1234-5678",
        "userAddress": "123 Main St, City, Country"
    })
    
    assert response.status_code == 200
    assert response.json()["resultCode"] == "SUCCESS"
    assert response.json()["message"] == "User registered successfully"


def test_register_user_duplicate_id(client):
    """
    ❌ 중복된 userId로 회원가입 시 실패

    Given: 이미 존재하는 userId가 있을 때
    When: 동일한 userId로 회원가입을 시도하면
    Then: 응답 상태 코드 400과 "User ID already exists" 오류 메시지를 반환해야 한다.
    """
    client.post("/user/register", json={
        "userId": "duplicateUser",
        "userPassword": "password123",
        "userEmail": "unique@example.com",
        "userName": "John Doe",
        "userPhoneNum": "010-5678-1234",
        "userAddress": "456 Second St, City, Country"
    })

    response = client.post("/user/register", json={
        "userId": "duplicateUser",  # 중복된 ID
        "userPassword": "password456",
        "userEmail": "another@example.com",
        "userName": "Jane Doe",
        "userPhoneNum": "010-5678-4321",
        "userAddress": "789 Third St, City, Country"
    })

    assert response.status_code == 400
    assert response.json()["detail"]["resultCode"] == "FAILURE"
    assert any(error["field"] == "userId" and error["message"] == "User ID already exists"
               for error in response.json()["detail"]["errors"])


def test_register_user_duplicate_email(client):
    """
    ❌ 중복된 이메일로 회원가입 시 실패

    Given: 이미 존재하는 userEmail이 있을 때
    When: 동일한 userEmail로 회원가입을 시도하면
    Then: 응답 상태 코드 400과 "Email is already registered" 오류 메시지를 반환해야 한다.
    """
    client.post("/user/register", json={
        "userId": "uniqueUser",
        "userPassword": "password123",
        "userEmail": "duplicate@example.com",
        "userName": "John Doe",
        "userPhoneNum": "010-5678-1234",
        "userAddress": "456 Second St, City, Country"
    })

    response = client.post("/user/register", json={
        "userId": "newUser",
        "userPassword": "password456",
        "userEmail": "duplicate@example.com",  # 중복된 이메일
        "userName": "Jane Doe",
        "userPhoneNum": "010-5678-4321",
        "userAddress": "789 Third St, City, Country"
    })

    assert response.status_code == 400
    assert response.json()["detail"]["resultCode"] == "FAILURE"
    assert any(error["field"] == "userEmail" and error["message"] == "Email is already registered"
               for error in response.json()["detail"]["errors"])


def test_register_user_empty_email(client):
    """
    ❌ 이메일이 빈 값일 때 회원가입 시 실패

    Given: 사용자가 이메일을 입력하지 않았을 때
    When: email 필드가 빈 문자열("")인 상태로 회원가입을 요청하면
    Then: 응답 상태 코드 422와 "value is not a valid email address" 오류 메시지를 반환해야 한다.
    """
    response = client.post("/user/register", json={
        "userId": "emptyEmailUser",
        "userPassword": "password123",
        "userEmail": "",  # 빈 값 입력
        "userName": "John Doe",
        "userPhoneNum": "010-1234-5678",
        "userAddress": "123 Main St, City, Country"
    })

    assert response.status_code == 422  # FastAPI가 자동으로 422 반환
    assert any(error["msg"] == "value is not a valid email address" for error in response.json()["detail"])


def test_register_user_invalid_email(client):
    """
    ❌ 잘못된 이메일 형식 입력 시 회원가입 실패

    Given: 사용자가 잘못된 이메일 형식을 입력했을 때
    When: "invalid-email"과 같은 잘못된 형식의 email을 회원가입 요청으로 보내면
    Then: 응답 상태 코드 422와 "value is not a valid email address" 오류 메시지를 반환해야 한다.
    """
    response = client.post("/user/register", json={
        "userId": "invalidEmailUser",
        "userPassword": "password123",
        "userEmail": "invalid-email",  # 잘못된 이메일 형식
        "userName": "John Doe",
        "userPhoneNum": "010-9876-5432",
        "userAddress": "Unknown Street, City, Country"
    })

    assert response.status_code == 422  # FastAPI의 데이터 검증 오류
