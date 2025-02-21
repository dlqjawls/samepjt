import pytest
import time
from app.core import config as settings_module
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

def test_refresh_token_success(client):
    """정상적인 토큰 갱신 테스트"""
    # Given: 회원가입된 사용자와 로그인된 상태
    register_payload = {
        "id": "refreshuser",
        "password": "test1234",
        "email": "refresh@example.com",
        "name": "토큰갱신테스트",
        "phoneNum": "010-1234-5678",
        "address": "Seoul, Korea"
    }
    client.post("/auth/register", json=register_payload)

    login_payload = {
        "id": "refreshuser",
        "password": "test1234"
    }
    login_response = client.post("/auth/login", json=login_payload)
    tokens = login_response.json()["data"]

    # When: 토큰 갱신 시도
    refresh_payload = {
        "refresh_token": tokens["refresh_token"]
    }
    response = client.post("/auth/refresh-token", json=refresh_payload)

    # Then: 응답 검증
    assert response.status_code == 200
    data = response.json()
    assert data["resultCode"] == "SUCCESS"
    assert "access_token" in data["data"]
    assert "refresh_token" in data["data"]

def test_refresh_token_invalid(client):
    """잘못된 리프레시 토큰으로 토큰 갱신 시도 테스트"""
    # Given: 잘못된 리프레시 토큰
    refresh_payload = {
        "refresh_token": "invalid_refresh_token"
    }

    # When: 토큰 갱신 시도
    response = client.post("/auth/refresh-token", json=refresh_payload)

    # Then: 401 Unauthorized 응답 검증
    assert response.status_code == 401
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "Invalid refresh token" in data["message"]

def test_refresh_token_expired(client, monkeypatch):
    """만료된 리프레시 토큰으로 토큰 갱신 시도 테스트"""
    
    # Given: 기존 환경 변수 백업
    original_access_expiry = settings_module.settings.ACCESS_TOKEN_EXPIRE_SECONDS
    original_refresh_expiry = settings_module.settings.REFRESH_TOKEN_EXPIRE_SECONDS

    # 환경 변수 변경 (importlib.reload() 사용 안 함)
    monkeypatch.setattr(settings_module.settings, "ACCESS_TOKEN_EXPIRE_SECONDS", 1)
    monkeypatch.setattr(settings_module.settings, "REFRESH_TOKEN_EXPIRE_SECONDS", 2)
    
    # Given: 회원가입된 사용자와 로그인된 상태
    register_payload = {
        "id": "expireduser",
        "password": "test1234",
        "email": "expired@example.com",
        "name": "만료테스트",
        "phoneNum": "010-1234-5678",
        "address": "Seoul, Korea"
    }
    client.post("/auth/register", json=register_payload)

    login_payload = {
        "id": "expireduser",
        "password": "test1234"
    }
    login_response = client.post("/auth/login", json=login_payload)
    tokens = login_response.json()["data"]

    # 토큰 만료 대기
    time.sleep(3)  # 3초 대기하여 토큰 만료

    # When: 만료된 리프레시 토큰으로 토큰 갱신 시도
    refresh_payload = {
        "refresh_token": tokens["refresh_token"]
    }
    response = client.post("/auth/refresh-token", json=refresh_payload)

    # Then: 401 Unauthorized 응답 검증
    assert response.status_code == 401
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "Refresh token has expired" in data["message"]

    # 환경 변수 복구
    monkeypatch.setattr(settings_module.settings, "ACCESS_TOKEN_EXPIRE_SECONDS", original_access_expiry)
    monkeypatch.setattr(settings_module.settings, "REFRESH_TOKEN_EXPIRE_SECONDS", original_refresh_expiry)

def test_logout_success(client):
    """정상적인 로그아웃 테스트"""
    # Given: 회원가입된 사용자와 로그인된 상태
    register_payload = {
        "id": "logoutuser",
        "password": "test1234",
        "email": "logout@example.com",
        "name": "로그아웃테스트",
        "phoneNum": "010-1234-5678",
        "address": "Seoul, Korea"
    }
    client.post("/auth/register", json=register_payload)

    login_payload = {
        "id": "logoutuser",
        "password": "test1234"
    }
    login_response = client.post("/auth/login", json=login_payload)
    access_token = login_response.json()["data"]["access_token"]

    # When: 로그아웃 시도
    response = client.post("/auth/logout", headers={"Authorization": f"Bearer {access_token}"})

    # Then: 응답 검증
    assert response.status_code == 200
    data = response.json()
    assert data["resultCode"] == "SUCCESS"

def test_logout_invalid_token(client):
    """잘못된 토큰으로 로그아웃 시도 테스트"""
    # Given: 잘못된 토큰
    invalid_token = "invalid_token_example"

    # When: 로그아웃 시도
    response = client.post("/auth/logout", headers={"Authorization": f"Bearer {invalid_token}"})

    # Then: 401 Unauthorized 응답 검증
    assert response.status_code == 401
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "Token is malformed" in data["message"]
    
    
def test_refresh_token_after_logout(client):
    """로그인 -> 로그아웃 -> 삭제된 리프레시 토큰으로 재발급 시도 테스트"""
    # Given: 회원가입된 사용자와 로그인된 상태
    register_payload = {
        "id": "testuser",
        "password": "test1234",
        "email": "test@example.com",
        "name": "테스트유저",
        "phoneNum": "010-1234-5678",
        "address": "Seoul, Korea"
    }
    client.post("/auth/register", json=register_payload)

    login_payload = {
        "id": "testuser",
        "password": "test1234"
    }
    login_response = client.post("/auth/login", json=login_payload)
    tokens = login_response.json()["data"]

    # When: 로그아웃 시도
    response = client.post("/auth/logout", headers={"Authorization": f"Bearer {tokens['access_token']}"})
    assert response.status_code == 200
    logout_data = response.json()
    assert logout_data["resultCode"] == "SUCCESS"

    # Then: 로그아웃 후 삭제된 리프레시 토큰으로 재발급 시도
    refresh_payload = {
        "refresh_token": tokens["refresh_token"]
    }
    response = client.post("/auth/refresh-token", json=refresh_payload)

    # 401 Unauthorized 응답 검증
    assert response.status_code == 401
    data = response.json()
    assert data["resultCode"] == "FAILURE"
    assert "Invalid refresh token" in data["message"]