import pytest
from app.core.jwt import jwt_handler

# --- Fixtures: 토큰 생성 ---
@pytest.fixture
def master_token():
    # JWTHandler의 create_token()은 (access_token, refresh_token)을 반환합니다.
    return jwt_handler.create_token(1, role="master")[0]

@pytest.fixture
def semi_admin_token():
    return jwt_handler.create_token(2, role="semi")[0]

@pytest.fixture
def non_admin_token():
    return jwt_handler.create_token(3, role="user")[0]


# --- 테스트 케이스 ---

def test_get_module_install_videos_success(client, master_token):
    """
    관리자(또는 일반 관리자) 토큰을 사용하여 모듈 설치 영상을 조회할 때,
    올바른 영상 목록(모두 video_type이 'module installation')이 반환되는지 검증합니다.
    """
    rent_id = 1
    response = client.get(
        f"/admin/rent-history/{rent_id}/module-install-videos",
        headers={"Authorization": f"Bearer {master_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["resultCode"] == "SUCCESS"
    videos = data["data"]["videos"]
    # 각 영상의 video_type이 module installation 인지 확인
    for video in videos:
        assert video["video_type"] == "module installation"


def test_get_autonomous_videos_success(client, master_token):
    """
    관리자(또는 일반 관리자) 토큰을 사용하여 자율주행 영상을 조회할 때,
    올바른 영상 목록(모두 video_type이 'autonomous driving')이 반환되는지 검증합니다.
    """
    rent_id = 1
    response = client.get(
        f"/admin/rent-history/{rent_id}/autonomous-videos",
        headers={"Authorization": f"Bearer {master_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["resultCode"] == "SUCCESS"
    videos = data["data"]["videos"]
    # 각 영상의 video_type이 autonomous driving 인지 확인
    for video in videos:
        assert video["video_type"] == "autonomous driving"


def test_get_module_install_videos_unauthenticated(client):
    """
    인증 토큰 없이 모듈 설치 영상 조회 시 401 Unauthorized가 반환되어야 합니다.
    """
    rent_id = 1
    response = client.get(f"/admin/rent-history/{rent_id}/module-install-videos")
    assert response.status_code == 401


def test_get_autonomous_videos_forbidden(client, non_admin_token):
    """
    권한이 없는 사용자(일반 사용자) 토큰으로 요청 시 403 Forbidden이 반환되어야 합니다.
    """
    rent_id = 1
    response = client.get(
        f"/admin/rent-history/{rent_id}/autonomous-videos",
        headers={"Authorization": f"Bearer {non_admin_token}"}
    )
    assert response.status_code == 403
