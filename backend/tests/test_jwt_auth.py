import pytest
from fastapi.testclient import TestClient
from app.main import app  # FastAPI 애플리케이션 import
from app.api.schemas.token import TokenRefreshRequest

client = TestClient(app)

@pytest.fixture
def admin_login():
    """ 관리자 계정(admin) 로그인 후 JWT 토큰 반환 """
    response = client.post("/admin/login", json={
        "adminId": "admin",
        "adminPassword": "admin123"
    })
    assert response.status_code == 200
    json_response = response.json()
    return json_response["accessToken"], json_response["refreshToken"]


@pytest.fixture
def semi_admin_login():
    """ 세미 관리자 계정(semi) 로그인 후 JWT 토큰 반환 """
    response = client.post("/admin/login", json={
        "adminId": "semi",
        "adminPassword": "semi123"
    })
    assert response.status_code == 200
    json_response = response.json()
    return json_response["accessToken"], json_response["refreshToken"]


def test_admin_access(admin_login):
    """ (Success) 관리자가 admin-only 엔드포인트에 접근 가능 """
    access_token, _ = admin_login
    response = client.get("/test/admin-only", headers={"Authorization": f"Bearer {access_token}"})
    
    assert response.status_code == 200
    assert response.json()["message"] == "관리자 전용 API"


def test_semi_admin_access(semi_admin_login):
    """ (Fail) 세미 관리자는 admin-only 엔드포인트에 접근 불가 """
    access_token, _ = semi_admin_login
    response = client.get("/test/admin-only", headers={"Authorization": f"Bearer {access_token}"})
    
    assert response.status_code == 403  # 접근 권한 없음
    assert response.json()["detail"] == "Permission denied"


def test_semi_admin_semi_access(semi_admin_login):
    """ (Success) 세미 관리자는 semi-admin 엔드포인트 접근 가능 """
    access_token, _ = semi_admin_login
    response = client.get("/test/semi-admin", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 200
    assert response.json()["message"] == "세미 관리자 및 관리자 전용 API"


def test_admin_semi_access(admin_login):
    """ (Success) 관리자는 semi-admin 엔드포인트 접근 가능 """
    access_token, _ = admin_login
    response = client.get("/test/semi-admin", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 200
    assert response.json()["message"] == "세미 관리자 및 관리자 전용 API"


def test_refresh_token(admin_login):
    """ ✅ (수정됨) 리프레시 토큰을 사용하여 새로운 액세스 토큰 발급 """
    _, refresh_token = admin_login
    request = TokenRefreshRequest(refresh_token=refresh_token)

    response = client.post("/auth/refresh-token", json=request.dict())

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()

def test_logout(admin_login):
    """ (Success) 로그아웃 후 리프레시 토큰 삭제 확인 """
    access_token, _ = admin_login
    response = client.post("/auth/logout", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 200
    assert response.json()["message"] == "Successfully logged out"
